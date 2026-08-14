import time
from typing import Dict, List, Any, Optional
from .order_models import OMSOrder, OMSFill
from .order_repository import OrderRepository
from .order_state_machine import OrderStateMachine, OrderState
from .smart_order_router import SmartOrderRouter
from .slippage_engine import SlippageEngine
from .fill_engine import FillEngine
from .partial_fill_manager import PartialFillManager, PartialFillTracker
from .twap_engine import TWAPEngine
from .vwap_engine import VWAPEngine
from .iceberg_engine import IcebergEngine
from .retry_engine import RetryEngine
from .failover_engine import FailoverEngine
from .exchange_health_monitor import ExchangeHealthMonitor
from .execution_cost_engine import ExecutionCostEngine
from .execution_telemetry import ExecutionTelemetry
from .pre_trade_checks import PreTradeChecksEngine
from .post_trade_processing import PostTradeProcessingEngine

class ExecutionOrchestrator:
    """Master Institutional OMS / EMS Execution Orchestrator Singleton."""

    def __init__(self):
        self.repository = OrderRepository()
        self.sor = SmartOrderRouter()
        self.slippage_engine = SlippageEngine()
        self.fill_engine = FillEngine()
        self.partial_fill_manager = PartialFillManager()
        self.twap_engine = TWAPEngine()
        self.vwap_engine = VWAPEngine()
        self.iceberg_engine = IcebergEngine()
        self.retry_engine = RetryEngine()
        self.failover_engine = FailoverEngine()
        self.health_monitor = ExchangeHealthMonitor()
        self.cost_engine = ExecutionCostEngine()
        self.telemetry = ExecutionTelemetry()
        self.pre_trade_checks = PreTradeChecksEngine()
        self.post_trade_processing = PostTradeProcessingEngine()

    def submit_order(
        self,
        user_id: str,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "MARKET",
        price: Optional[float] = None,
        exchange: Optional[str] = None
    ) -> Dict[str, Any]:
        """Single Gateway for Order Creation & Execution."""
        # 1. Create Order in DRAFT state
        order = OMSOrder(
            user_id=str(user_id),
            symbol=symbol,
            side=side.upper(),
            order_type=order_type.upper(),
            quantity=quantity,
            price=price,
            exchange=exchange.upper() if exchange else "BINANCE"
        )
        sm = OrderStateMachine(order.order_id, OrderState.DRAFT)
        self.repository.save_order(order)

        # 2. Validate Order
        sm.transition_to(OrderState.VALIDATED, reason="Pre-trade validation passed")
        order.status = sm.current_state.value

        # 3. Pre-Trade Checks & Slippage Protection
        curr_price = price if (price and price > 0) else 50000.0
        checks = self.pre_trade_checks.run_pre_trade_checks(order, current_price=curr_price)
        if not checks["passed"]:
            sm.transition_to(OrderState.REJECTED, reason=checks["reason"])
            order.status = sm.current_state.value
            self.repository.save_order(order)
            return {"status": "rejected", "reason": checks["reason"], "order": order.to_dict()}

        # 4. Smart Order Routing
        sm.transition_to(OrderState.ROUTING, reason="Selecting best venue via SOR")
        order.status = sm.current_state.value
        best_venue = self.sor.route_order(symbol, side, quantity, order_type, exchange, curr_price)
        order.exchange = best_venue.exchange

        # 5. Submit to Venue
        sm.transition_to(OrderState.SUBMITTED, reason=f"Submitted to {order.exchange}")
        order.status = sm.current_state.value
        order.exchange_order_id = f"EX-{order.order_id}"

        # 6. Execute Fills (Market Order Full Fill Execution)
        fill_price = best_venue.ask if side.upper() in ["BUY", "LONG"] else best_venue.bid
        fill = self.fill_engine.execute_fill(order, fill_price=fill_price, fill_quantity=quantity)
        self.repository.save_fill(fill)

        # Update Order State
        order.filled_quantity = fill.fill_quantity
        order.remaining_quantity = max(0.0, order.quantity - fill.fill_quantity)
        order.average_fill_price = fill.fill_price

        if order.remaining_quantity <= 0.0:
            sm.transition_to(OrderState.FILLED, reason="Order fully executed")
            order.status = sm.current_state.value
        else:
            sm.transition_to(OrderState.PARTIALLY_FILLED, reason="Order partially filled")
            order.status = sm.current_state.value

        self.repository.save_order(order)

        # 7. Post-Trade Cost Analysis & Telemetry
        post_res = self.post_trade_processing.process_completed_order(order, expected_price=curr_price, total_fee_usd=fill.fee)
        telemetry_payload = self.telemetry.format_execution_update(
            order_id=order.order_id,
            status=order.status,
            filled_qty=order.filled_quantity,
            remaining_qty=order.remaining_quantity,
            avg_fill_price=order.average_fill_price,
            exchange=order.exchange
        )

        return {
            "status": "success",
            "order": order.to_dict(),
            "fill": fill.to_dict(),
            "cost_analysis": post_res.get("cost_analysis", {}),
            "telemetry": telemetry_payload
        }

    def cancel_order(self, order_id: str, reason: str = "User cancel request") -> Dict[str, Any]:
        order = self.repository.get_order(order_id)
        if not order:
            return {"status": "error", "message": f"Order {order_id} not found"}

        if order.status in [OrderState.FILLED.value, OrderState.CANCELLED.value, OrderState.REJECTED.value]:
            return {"status": "error", "message": f"Cannot cancel order in terminal state {order.status}"}

        sm = OrderStateMachine(order.order_id, OrderState(order.status))
        sm.transition_to(OrderState.CANCELLED, reason=reason)
        order.status = sm.current_state.value
        self.repository.save_order(order)
        return {"status": "success", "order": order.to_dict()}

# Global Singleton Orchestrator
execution_orchestrator = ExecutionOrchestrator()
