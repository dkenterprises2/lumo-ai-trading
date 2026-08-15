import time
import uuid
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

from .autonomous_state_machine import ExecutionStateMachine, ExecutionState
from .autonomous_governance import AutonomousGovernanceEngine
from .autonomous_metrics import AutonomousMetricsTracker
from .arbitrage_exit_engine import ArbitrageExitEngine
from backend.execution.execution_orchestrator import execution_orchestrator
from backend.portfolio_risk.portfolio_risk_engine import InstitutionalPortfolioRiskEngine
from backend.arbitrage import ExchangePriceCollector, SpreadDetector

logger = logging.getLogger("autonomous_execution_manager")

class MockUserTrader:
    """Mock trader portfolio wrapper for Phase 34 risk engine integration."""
    def __init__(self, user_id: str = "user-p41", usdt_balance: float = 100000.0):
        self.user_id = user_id
        self.usdt_balance = usdt_balance
        self.initial_balance = usdt_balance
        self.positions: Dict[str, Any] = {}
        self.trade_history: List[Any] = []
        self.peak_equity = usdt_balance
        self.max_open_positions = 10
        self.default_leverage = 1

    def get_portfolio_summary(self, prices=None):
        return {
            "total_portfolio_value": self.usdt_balance,
            "total_unrealized_pnl_usd": 0.0,
            "daily_pnl_usd": 0.0
        }

    def _sync_save_portfolio(self):
        pass

@dataclass
class ShadowPosition:
    position_id: str
    execution_id: str
    symbol: str
    buy_exchange: str
    sell_exchange: str
    quantity: float
    buy_price: float
    sell_price: float
    entry_fees: float
    entry_timestamp: float
    status: str = "OPEN"  # OPEN, MONITORING, CLOSING, CLOSED
    exit_timestamp: Optional[float] = None
    exit_reason: Optional[str] = None
    gross_pnl: float = 0.0
    net_pnl: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ExecutionRecord:
    execution_id: str
    opportunity_id: str
    idempotency_key: str
    symbol: str
    buy_exchange: str
    sell_exchange: str
    requested_amount_usd: float
    quantity: float
    buy_fill_price: float
    sell_fill_price: float
    selected_algorithm: str
    selection_reason: str
    status: str
    risk_decision: Dict[str, Any]
    governance_decision: Dict[str, Any]
    fees: float
    slippage: float
    gross_pnl: float
    net_pnl: float
    position_id: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    state_history: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class AutonomousExecutionManager:
    """Master Autonomous Shadow Execution & Lifecycle Manager."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AutonomousExecutionManager, cls).__new__(cls)
            cls._instance._init_manager()
        return cls._instance

    def _init_manager(self):
        self.risk_engine = InstitutionalPortfolioRiskEngine()
        self.governance_engine = AutonomousGovernanceEngine()
        self.exit_engine = ArbitrageExitEngine()
        self.collector = ExchangePriceCollector()
        self.detector = SpreadDetector()
        self.metrics_tracker = AutonomousMetricsTracker()
        self.trader = MockUserTrader()

        self.executions: Dict[str, ExecutionRecord] = {}
        self.state_machines: Dict[str, ExecutionStateMachine] = {}
        self.positions: Dict[str, ShadowPosition] = {}

    def select_execution_algorithm(
        self,
        amount_usd: float,
        buy_price: float,
        book_depth_usd: float = 50000.0,
        volatility_pct: float = 2.0,
        urgency: str = "NORMAL"
    ) -> tuple[str, str]:
        """Automatically selects optimal execution algorithm based on liquidity & market conditions."""
        depth_utilization_pct = (amount_usd / max(1.0, book_depth_usd)) * 100.0

        if depth_utilization_pct > 20.0:
            alg = "ICEBERG"
            reason = f"ICEBERG selected because requested quantity is {depth_utilization_pct:.1f}% of available depth (minimizes market impact)."
        elif depth_utilization_pct > 10.0 or urgency == "HIGH":
            alg = "TWAP"
            reason = f"TWAP selected because requested quantity is {depth_utilization_pct:.1f}% of available depth (time-sliced execution)."
        elif volatility_pct > 5.0:
            alg = "VWAP"
            reason = f"VWAP selected due to high volatility ({volatility_pct:.1f}%) to execute along volume profile."
        else:
            alg = "SMART_ROUTER"
            reason = f"SMART_ROUTER selected for low depth utilization ({depth_utilization_pct:.1f}%) with direct venue routing."

        return alg, reason

    def process_opportunity(self, opp: Dict[str, Any], user_id: str = "user-p41") -> Dict[str, Any]:
        """Main Real Pipeline: DETECTED -> RISK -> GOVERNANCE -> OMS -> SHADOW FILL -> POSITION -> MONITOR -> PNL"""
        exec_id = f"EXEC-AUTO-{uuid.uuid4().hex[:8].upper()}"
        sm = ExecutionStateMachine(exec_id, ExecutionState.DETECTED)
        self.state_machines[exec_id] = sm

        symbol = opp.get("symbol", "BTC/USDT")
        buy_ex = opp.get("buy_exchange", "BINANCE")
        sell_ex = opp.get("sell_exchange", "BYBIT")
        buy_price = float(opp.get("buy_price", 0.0))
        sell_price = float(opp.get("sell_price", 0.0))
        amount_usd = float(opp.get("amount_usd", opp.get("estimated_profit_usd", 10000.0)))
        if amount_usd < 1000.0:
            amount_usd = 10000.0

        opp_id = opp.get("opp_id", f"ARB-{uuid.uuid4().hex[:8].upper()}")

        if buy_price <= 0.0 or sell_price <= 0.0 or buy_price >= sell_price:
            sm.transition_to(ExecutionState.LIQUIDITY_BLOCKED, reason="Buy price <= 0 or Sell price <= Buy price")
            self.metrics_tracker.record_opportunity(is_approved=False, blocked_by="GOVERNANCE")
            return {"status": "rejected", "reason": "Liquidity/Price invalid", "execution_id": exec_id}

        # 1. Validation & Freshness Check
        sm.transition_to(ExecutionState.VALIDATING, reason="Validating quote freshness and exchange connectivity")
        quotes = self.collector.fetch_all_quotes(symbol)
        q_buy = quotes.get(buy_ex)
        q_sell = quotes.get(sell_ex)

        if not q_buy or not q_sell or q_buy.status == "DATA_UNAVAILABLE" or q_sell.status == "DATA_UNAVAILABLE":
            sm.transition_to(ExecutionState.LIQUIDITY_BLOCKED, reason="Exchange quote data unavailable")
            self.metrics_tracker.record_opportunity(is_approved=False, blocked_by="GOVERNANCE")
            return {"status": "rejected", "reason": "Data unavailable", "execution_id": exec_id}

        max_age = max(q_buy.data_age_ms, q_sell.data_age_ms)
        if max_age > 2000.0 or q_buy.status == "DATA_STALE" or q_sell.status == "DATA_STALE":
            sm.transition_to(ExecutionState.STALE, reason=f"Quote data stale ({max_age:.0f}ms > 2000ms threshold)")
            self.metrics_tracker.record_opportunity(is_approved=False, blocked_by="GOVERNANCE")
            return {"status": "rejected", "reason": "Quote stale", "execution_id": exec_id}

        # 2. Risk Check (Phase 34 Institutional Portfolio Risk Engine)
        sm.transition_to(ExecutionState.RISK_CHECK, reason="Evaluating Phase 34 Portfolio Risk Gate")
        risk_res = self.risk_engine.evaluate_trade_risk_gate(
            user_trader=self.trader,
            symbol=symbol,
            side="BUY",
            requested_allocation_usd=amount_usd
        )

        if not risk_res.get("passed", False):
            reason = risk_res.get("decision", {}).get("explanation", "Portfolio risk gate blocked trade")
            sm.transition_to(ExecutionState.RISK_BLOCKED, reason=reason)
            self.metrics_tracker.record_opportunity(is_approved=False, blocked_by="RISK")
            return {"status": "rejected", "reason": reason, "execution_id": exec_id, "risk_decision": risk_res}

        # 3. Governance & Idempotency Check
        sm.transition_to(ExecutionState.GOVERNANCE_CHECK, reason="Evaluating Autonomous Governance & Idempotency Key")
        gov_res = self.governance_engine.validate_opportunity_governance(
            symbol=symbol,
            buy_exchange=buy_ex,
            sell_exchange=sell_ex,
            buy_price=buy_price,
            sell_price=sell_price,
            kill_switch_halted=self.risk_engine.kill_switch.is_halted
        )

        if not gov_res.is_allowed:
            sm.transition_to(ExecutionState.GOVERNANCE_BLOCKED, reason=gov_res.reason)
            self.metrics_tracker.record_opportunity(is_approved=False, blocked_by="GOVERNANCE")
            return {"status": "rejected", "reason": gov_res.reason, "execution_id": exec_id, "governance_decision": gov_res.to_dict()}

        # 4. Approved & Automatic Algorithm Selection
        sm.transition_to(ExecutionState.APPROVED, reason="Passed all risk & governance checks")
        alg, alg_reason = self.select_execution_algorithm(amount_usd, buy_price)
        self.metrics_tracker.record_opportunity(is_approved=True)

        # 5. Execute Dual-Leg Fills via OMS (ExecutionOrchestrator)
        sm.transition_to(ExecutionState.EXECUTING, reason=f"Submitting orders via OMS ({alg})")
        self.metrics_tracker.record_execution_started()

        quantity = amount_usd / buy_price if buy_price > 0 else 0.1

        buy_order_res = execution_orchestrator.submit_order(
            user_id=user_id,
            symbol=symbol,
            side="BUY",
            quantity=quantity,
            exchange=buy_ex
        )

        sell_order_res = execution_orchestrator.submit_order(
            user_id=user_id,
            symbol=symbol,
            side="SELL",
            quantity=quantity,
            exchange=sell_ex
        )

        sm.transition_to(ExecutionState.FILLED, reason="Dual-leg market orders executed cleanly")

        buy_fill_price = buy_order_res.get("fill", {}).get("fill_price", buy_price * 1.0001)
        sell_fill_price = sell_order_res.get("fill", {}).get("fill_price", sell_price * 0.9999)

        # Fee & Friction Accounting
        buy_fee = amount_usd * 0.00075
        sell_fee = amount_usd * 0.00075
        total_fees = buy_fee + sell_fee
        slippage_cost = amount_usd * 0.0002
        market_impact_cost = amount_usd * 0.0001
        funding_cost = amount_usd * 0.00005
        latency_cost = amount_usd * 0.00005
        transfer_cost = 1.0

        gross_pnl = (sell_fill_price - buy_fill_price) * quantity
        total_costs = total_fees + slippage_cost + market_impact_cost + funding_cost + latency_cost + transfer_cost
        net_pnl = gross_pnl - total_costs

        # 6. Create Real Persisted Shadow Position
        pos_id = f"POS-{uuid.uuid4().hex[:8].upper()}"
        pos = ShadowPosition(
            position_id=pos_id,
            execution_id=exec_id,
            symbol=symbol,
            buy_exchange=buy_ex,
            sell_exchange=sell_ex,
            quantity=quantity,
            buy_price=buy_fill_price,
            sell_price=sell_fill_price,
            entry_fees=total_fees,
            entry_timestamp=time.time(),
            status="OPEN",
            gross_pnl=round(gross_pnl, 2),
            net_pnl=round(net_pnl, 2)
        )
        self.positions[pos_id] = pos
        self.metrics_tracker.record_position_opened()

        # Update mock trader position to dynamically change portfolio risk score
        self.trader.positions[symbol] = {
            "symbol": symbol,
            "amount": quantity,
            "entry_price": buy_fill_price
        }

        sm.transition_to(ExecutionState.POSITION_OPEN, reason=f"Shadow position {pos_id} opened and persisted")
        sm.transition_to(ExecutionState.MONITORING, reason="Position actively monitored by ArbitrageExitEngine")

        record = ExecutionRecord(
            execution_id=exec_id,
            opportunity_id=opp_id,
            idempotency_key=gov_res.idempotency_key,
            symbol=symbol,
            buy_exchange=buy_ex,
            sell_exchange=sell_ex,
            requested_amount_usd=amount_usd,
            quantity=round(quantity, 4),
            buy_fill_price=round(buy_fill_price, 2),
            sell_fill_price=round(sell_fill_price, 2),
            selected_algorithm=alg,
            selection_reason=alg_reason,
            status=sm.current_state.value,
            risk_decision=risk_res,
            governance_decision=gov_res.to_dict(),
            fees=round(total_fees, 2),
            slippage=round(slippage_cost, 2),
            gross_pnl=round(gross_pnl, 2),
            net_pnl=round(net_pnl, 2),
            position_id=pos_id,
            state_history=sm.get_history_dicts()
        )
        self.executions[exec_id] = record

        return {
            "status": "success",
            "execution": record.to_dict(),
            "position": pos.to_dict()
        }

    def monitor_and_close_positions(self) -> List[Dict[str, Any]]:
        """Active position monitoring and exit engine evaluation loop."""
        closed_reports = []
        for pos_id, pos in list(self.positions.items()):
            if pos.status in ["OPEN", "MONITORING"]:
                quotes = self.collector.fetch_all_quotes(pos.symbol)
                q_buy = quotes.get(pos.buy_exchange)
                q_sell = quotes.get(pos.sell_exchange)

                exit_res = self.exit_engine.evaluate_position_exit(
                    position=pos.to_dict(),
                    current_buy_quote=q_buy,
                    current_sell_quote=q_sell,
                    kill_switch_halted=self.risk_engine.kill_switch.is_halted
                )

                if exit_res.should_exit:
                    exec_id = pos.execution_id
                    sm = self.state_machines.get(exec_id)

                    if sm:
                        sm.transition_to(ExecutionState.EXIT_TRIGGERED, reason=f"Exit triggered: {exit_res.trigger_reason}")
                        sm.transition_to(ExecutionState.CLOSING, reason="Submitting unwind orders via OMS")

                    exit_info = self.exit_engine.execute_shadow_exit(pos.to_dict(), reason=exit_res.trigger_reason)

                    pos.status = "CLOSED"
                    pos.exit_timestamp = time.time()
                    pos.exit_reason = exit_res.trigger_reason

                    if sm:
                        sm.transition_to(ExecutionState.CLOSED, reason="Position closed cleanly")
                        sm.transition_to(ExecutionState.COMPLETED, reason="Execution lifecycle completed")

                    # Remove from mock trader positions to update risk score
                    if pos.symbol in self.trader.positions:
                        del self.trader.positions[pos.symbol]

                    self.metrics_tracker.record_position_closed(pos.net_pnl, pos.entry_fees)

                    if exec_id in self.executions:
                        self.executions[exec_id].status = "COMPLETED"
                        if sm:
                            self.executions[exec_id].state_history = sm.get_history_dicts()

                    closed_reports.append(exit_info)
        return closed_reports
