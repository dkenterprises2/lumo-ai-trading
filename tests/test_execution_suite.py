import pytest
from backend.execution import (
    OrderStateMachine,
    OrderState,
    SmartOrderRouter,
    SlippageEngine,
    ExecutionOrchestrator
)
from backend.execution.order_state_machine import InvalidStateTransitionError
from backend.execution.order_models import OMSOrder
from backend.execution.twap_engine import TWAPEngine
from backend.execution.vwap_engine import VWAPEngine
from backend.execution.iceberg_engine import IcebergEngine
from backend.execution.partial_fill_manager import PartialFillManager, PartialFillTracker
from backend.execution.retry_engine import RetryEngine
from backend.execution.failover_engine import FailoverEngine
from backend.execution.execution_cost_engine import ExecutionCostEngine
from backend.execution.execution_telemetry import ExecutionTelemetry
from backend.execution.exchange_health_monitor import ExchangeHealthMonitor
from backend.execution.execution_governance import ExecutionGovernance

# 1. State Machine Transitions
def test_valid_state_machine_transitions():
    sm = OrderStateMachine("ORD-1", OrderState.DRAFT)
    assert sm.current_state == OrderState.DRAFT
    sm.transition_to(OrderState.VALIDATED)
    assert sm.current_state == OrderState.VALIDATED
    sm.transition_to(OrderState.ROUTING)
    assert sm.current_state == OrderState.ROUTING
    sm.transition_to(OrderState.SUBMITTED)
    assert sm.current_state == OrderState.SUBMITTED
    sm.transition_to(OrderState.FILLED)
    assert sm.current_state == OrderState.FILLED

# 2. Invalid State Transitions
def test_invalid_state_machine_transition_raises():
    sm = OrderStateMachine("ORD-2", OrderState.DRAFT)
    with pytest.raises(InvalidStateTransitionError):
        sm.transition_to(OrderState.FILLED)  # DRAFT -> FILLED is illegal

def test_terminal_state_transition_raises():
    sm = OrderStateMachine("ORD-3", OrderState.FILLED)
    with pytest.raises(InvalidStateTransitionError):
        sm.transition_to(OrderState.CANCELLED)

# 3. Smart Order Routing Scoring
def test_smart_order_router_scoring():
    sor = SmartOrderRouter()
    score = sor.route_order("BTC/USDT", "BUY", 1.0)
    assert score.exchange in sor.SUPPORTED_EXCHANGES
    assert score.score > 0.0

def test_smart_order_router_requested_exchange():
    sor = SmartOrderRouter()
    score = sor.route_order("BTC/USDT", "BUY", 1.0, requested_exchange="BYBIT")
    assert score.exchange == "BYBIT"

# 4. Slippage Protection & Blocking
def test_slippage_engine_allow():
    engine = SlippageEngine()
    est = engine.estimate_slippage("BTC/USDT", "BUY", 0.01, price=50000.0, available_liquidity_usd=1000000.0)
    assert est.action == "ALLOW"

def test_slippage_engine_blocking():
    engine = SlippageEngine()
    est = engine.estimate_slippage("BTC/USDT", "BUY", 50.0, price=50000.0, available_liquidity_usd=10000.0)
    assert est.action == "BLOCK"
    assert est.estimated_slippage_pct > 0.50

# 5. TWAP Slicing
def test_twap_slice_generation():
    engine = TWAPEngine()
    job = engine.create_twap_job("TWAP-1", "BTC/USDT", "BUY", 10.0, duration_seconds=300, slice_interval_seconds=30)
    assert job.num_slices == 10
    assert len(job.slices) == 10
    assert job.slices[0].quantity == 1.0

# 6. VWAP Volume Allocation
def test_vwap_profile_allocation():
    engine = VWAPEngine()
    job = engine.create_vwap_job("VWAP-1", "ETH/USDT", "BUY", 100.0, num_bins=10)
    assert job.num_bins == 10
    total_alloc = sum(s.allocated_quantity for s in job.slices)
    assert abs(total_alloc - 100.0) < 0.1

# 7. Iceberg Replenishment
def test_iceberg_slice_replenishment():
    engine = IcebergEngine()
    state = engine.create_iceberg("ICE-1", "BTC/USDT", "BUY", 10.0, display_quantity_pct=10.0)
    assert state.display_quantity == 1.0
    assert state.remaining_quantity == 10.0

    # Fill slice
    next_state = engine.process_slice_fill(state, 1.0)
    assert next_state.filled_quantity == 1.0
    assert next_state.remaining_quantity == 9.0
    assert next_state.num_replenishments == 1

# 8. Partial Fill Aggregation
def test_partial_fill_manager_aggregation():
    mgr = PartialFillManager()
    tracker = PartialFillTracker("ORD-10", 10.0, 0.0, 10.0, 0.0, 0, 0.0, "PARTIAL")

    t1 = mgr.process_fill(tracker, 4.0, 50000.0)
    assert t1.filled_qty == 4.0
    assert t1.remaining_qty == 6.0
    assert t1.average_fill_price == 50000.0

    t2 = mgr.process_fill(t1, 6.0, 51000.0)
    assert t2.filled_qty == 10.0
    assert t2.remaining_qty == 0.0
    assert t2.status == "COMPLETED"

# 9. Retry Exponential Backoff
def test_retry_engine_backoff():
    engine = RetryEngine()
    assert engine.calculate_backoff(1) == 1.0
    assert engine.calculate_backoff(2) == 2.0
    assert engine.calculate_backoff(3) == 4.0
    assert engine.calculate_backoff(4) == 8.0
    assert engine.calculate_backoff(5) == -1.0  # Max attempts

def test_transient_error_detection():
    engine = RetryEngine()
    assert engine.is_transient_error(Exception("429 rate limit exceeded")) is True
    assert engine.is_transient_error(Exception("Invalid signature")) is False

# 10. Failover Rerouting
def test_failover_engine_rerouting():
    engine = FailoverEngine()
    event = engine.evaluate_failover("ORD-1", "CL-1", "BINANCE", ["BINANCE", "BYBIT", "OKX"])
    assert event is not None
    assert event.primary_exchange == "BINANCE"
    assert event.failover_exchange == "BYBIT"

# 11. Execution Cost Calculations
def test_execution_cost_decomposition():
    engine = ExecutionCostEngine()
    cost = engine.compute_cost_analysis("ORD-5", expected_price=50000.0, actual_average_fill=50050.0, quantity=1.0, side="BUY")
    assert cost.slippage_cost_usd == 50.0
    assert cost.implementation_shortfall_bps == 10.0
    assert cost.total_execution_cost_usd > 50.0

# 12. Exchange Health Monitor
def test_exchange_health_monitor():
    monitor = ExchangeHealthMonitor()
    health = monitor.get_health("BINANCE")
    assert health.is_online is True
    assert health.status == "OPERATIONAL"

# 13. Execution Telemetry Formatting
def test_telemetry_formatting():
    telem = ExecutionTelemetry()
    update = telem.format_execution_update("ORD-1", "FILLED", 1.0, 0.0, 50000.0, "BINANCE")
    assert update["type"] == "execution_update"
    assert update["status"] == "FILLED"

# 14. Governance Pre-trade Validation
def test_execution_governance_validation():
    gov = ExecutionGovernance()
    order = OMSOrder(quantity=1.0, symbol="BTC/USDT")
    res = gov.validate_pre_trade_policy(order)
    assert res["passed"] is True

# 15–25. End-to-End Execution Flow Tests
def test_end_to_end_submit_order_filled():
    orchestrator = ExecutionOrchestrator()
    res = orchestrator.submit_order("user_1", "BTC/USDT", "BUY", 0.1, price=50000.0)
    assert res["status"] == "success"
    assert res["order"]["status"] == "FILLED"
    assert res["fill"]["fill_quantity"] == 0.1

def test_end_to_end_submit_order_rejected_by_slippage():
    orchestrator = ExecutionOrchestrator()
    res = orchestrator.submit_order("user_1", "BTC/USDT", "BUY", 100.0, price=50000.0)
    assert res["status"] == "rejected"
    assert "BLOCKED" in res["reason"] or "slippage" in res["reason"].lower()

def test_cancel_order():
    orchestrator = ExecutionOrchestrator()
    order = OMSOrder(user_id="1", symbol="BTC/USDT", side="BUY", quantity=1.0, status=OrderState.SUBMITTED.value)
    orchestrator.repository.save_order(order)
    res = orchestrator.cancel_order(order.order_id)
    assert res["status"] == "success"
    assert res["order"]["status"] == "CANCELLED"

def test_repository_list_orders():
    orchestrator = ExecutionOrchestrator()
    orchestrator.submit_order("user_99", "ETH/USDT", "BUY", 1.0, price=3000.0)
    orders = orchestrator.repository.list_orders("user_99")
    assert len(orders) >= 1

def test_stalled_fill_detection():
    mgr = PartialFillManager()
    tracker = PartialFillTracker("ORD-88", 10.0, 5.0, 5.0, 50000.0, 1, 1000000.0, "PARTIAL")
    assert mgr.check_stalled_fill(tracker, stall_timeout_seconds=60.0) is True

def test_failover_returns_none_if_no_candidates():
    engine = FailoverEngine()
    event = engine.evaluate_failover("ORD-1", "CL-1", "BINANCE", ["BINANCE"])
    assert event is None

def test_order_repository_fills():
    orchestrator = ExecutionOrchestrator()
    res = orchestrator.submit_order("user_10", "SOL/USDT", "BUY", 5.0, price=150.0)
    fills = orchestrator.repository.get_fills_for_order(res["order"]["order_id"])
    assert len(fills) == 1

def test_telemetry_slippage_warning():
    telem = ExecutionTelemetry()
    warn = telem.format_slippage_warning("ORD-1", 0.35, "REQUIRE_CONFIRMATION")
    assert warn["type"] == "slippage_warning"
    assert warn["action"] == "REQUIRE_CONFIRMATION"

def test_order_models_post_init():
    order = OMSOrder(quantity=5.0)
    assert order.remaining_quantity == 5.0

def test_market_impact_calculation():
    from backend.execution.market_impact_engine import MarketImpactEngine
    engine = MarketImpactEngine()
    bps = engine.estimate_impact_bps(10000.0, 10000000.0)
    assert bps > 0.0

def test_liquidity_engine_depth():
    from backend.execution.liquidity_engine import LiquidityEngine
    engine = LiquidityEngine()
    depth = engine.get_venue_liquidity("BINANCE", "BTC/USDT")
    assert depth == 500000.0
