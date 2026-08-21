import time
from typing import Dict, List, Any, Optional
from .order_models import OMSOrder, OMSFill
from .order_repository import OrderRepository
from .order_state_machine import OrderStateMachine, OrderState
from .smart_order_router import SmartOrderRouter
from .slippage_engine import SlippageEngine
from .fill_engine import FillEngine
from .partial_fill_manager import PartialFillManager
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
from .execution_planner import execution_planner, AutonomousExecutionPlanner

from backend.execution.execution_intent import ExecutionIntent
from backend.execution.adapters import (
    PaperExecutionAdapter,
    ShadowExecutionAdapter,
    LiveExchangeAdapter,
    ExecutionReceipt
)

class ExecutionOrchestrator:
    """Master Institutional OMS / EMS Execution Orchestrator Singleton with Parity Architecture."""

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
        self.execution_planner = execution_planner
        
        # Modular Execution Adapters
        self.paper_adapter = PaperExecutionAdapter()
        self.shadow_adapter = ShadowExecutionAdapter()
        self.live_adapter = LiveExchangeAdapter()

    def get_adapter(self, mode: str = "PAPER"):
        mode_upper = mode.upper()
        if mode_upper == "LIVE":
            return self.live_adapter
        elif mode_upper == "SHADOW":
            return self.shadow_adapter
        return self.paper_adapter

    def submit_order(
        self,
        user_id: str,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "MARKET",
        price: Optional[float] = None,
        exchange: Optional[str] = None,
        urgency: str = "NORMAL",
        is_arbitrage: bool = False,
        execution_mode: str = "PAPER",
        intent: Optional[ExecutionIntent] = None
    ) -> Dict[str, Any]:
        """Single Gateway for Order Creation & Execution with Parity Intent Architecture."""
        curr_price = price if (price and price > 0) else 50000.0
        
        # 1. Deterministic Execution Intent Object
        if intent is None:
            intent = ExecutionIntent(
                symbol=symbol,
                side=side.upper(),
                quantity=quantity,
                allocation_usd=round(quantity * curr_price, 2),
                order_type=order_type.upper(),
                execution_algorithm="DIRECT",
                target_price=curr_price,
                limit_price=price if order_type.upper() == "LIMIT" else None,
                urgency=urgency,
                execution_mode=execution_mode.upper()
            )

        # 2. Create Order in DRAFT state
        order = OMSOrder(
            user_id=str(user_id),
            symbol=intent.symbol,
            side=intent.side.upper(),
            order_type=intent.order_type.upper(),
            quantity=intent.quantity,
            price=intent.limit_price or intent.target_price,
            exchange=exchange.upper() if exchange else "BINANCE"
        )
        sm = OrderStateMachine(order.order_id, OrderState.DRAFT)
        self.repository.save_order(order)

        # 3. Generate Execution Plan via Autonomous Execution Planner
        plan = self.execution_planner.plan_order_execution(
            order_id=order.order_id,
            user_id=str(user_id),
            symbol=intent.symbol,
            side=intent.side,
            quantity=intent.quantity,
            current_price=curr_price,
            book_depth_usd=50000.0,
            volatility_pct=2.0,
            urgency=intent.urgency,
            is_arbitrage=is_arbitrage,
            execution_mode=intent.execution_mode
        )
        order.metadata["execution_plan"] = plan.to_dict()
        order.metadata["execution_intent"] = intent.to_dict()
        order.metadata["intent_hash"] = intent.to_hash()

        if plan.status == "REJECTED":
            sm.transition_to(OrderState.REJECTED, reason=plan.reason)
            order.status = sm.current_state.value
            self.repository.save_order(order)
            return {"status": "rejected", "reason": plan.reason, "order": order.to_dict(), "plan": plan.to_dict(), "intent": intent.to_dict()}

        # 4. Pre-Trade Validation & Slippage Checks
        sm.transition_to(OrderState.VALIDATED, reason="Pre-trade validation passed")
        order.status = sm.current_state.value

        checks = self.pre_trade_checks.run_pre_trade_checks(order, current_price=curr_price)
        if not checks["passed"]:
            sm.transition_to(OrderState.REJECTED, reason=checks["reason"])
            order.status = sm.current_state.value
            self.repository.save_order(order)
            return {"status": "rejected", "reason": checks["reason"], "order": order.to_dict(), "intent": intent.to_dict()}

        # 5. Smart Order Routing (Venue Selection)
        sm.transition_to(OrderState.ROUTING, reason="Selecting best venue via SOR")
        order.status = sm.current_state.value
        best_venue = self.sor.route_order(intent.symbol, intent.side, intent.quantity, intent.order_type, exchange, curr_price)
        order.exchange = best_venue.exchange

        # 6. Submit to Execution Adapter
        sm.transition_to(OrderState.SUBMITTED, reason=f"Submitted to {intent.execution_mode} adapter")
        order.status = sm.current_state.value
        
        adapter = self.get_adapter(intent.execution_mode)
        receipt: ExecutionReceipt = adapter.execute(intent)

        if receipt.status in ["REJECTED", "FAILED"]:
            sm.transition_to(OrderState.REJECTED, reason=receipt.rejection_reason or "Adapter rejection")
            order.status = sm.current_state.value
            self.repository.save_order(order)
            return {"status": "rejected", "reason": receipt.rejection_reason, "receipt": receipt.to_dict(), "order": order.to_dict()}

        # 7. Record Fill in Repository
        fill = self.fill_engine.execute_fill(order, fill_price=receipt.average_fill_price, fill_quantity=receipt.executed_quantity)
        self.repository.save_fill(fill)

        order.filled_quantity = receipt.executed_quantity
        order.remaining_quantity = max(0.0, order.quantity - receipt.executed_quantity)
        order.average_fill_price = receipt.average_fill_price
        order.exchange_order_id = receipt.exchange_order_id

        if order.remaining_quantity <= 0.0:
            sm.transition_to(OrderState.FILLED, reason="Order fully executed")
        else:
            sm.transition_to(OrderState.PARTIALLY_FILLED, reason="Order partially filled")
        order.status = sm.current_state.value
        self.repository.save_order(order)

        # 8. Post-Trade Cost Analysis & Telemetry
        post_res = self.post_trade_processing.process_completed_order(order, expected_price=curr_price, total_fee_usd=receipt.fees_usd)
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
            "receipt": receipt.to_dict(),
            "intent": intent.to_dict(),
            "intent_hash": intent.to_hash(),
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
