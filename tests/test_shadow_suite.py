import pytest
import asyncio
from backend.shadow_trading import (
    TradingMode, ShadowSafetyGuard, ShadowTradingViolation, shadow_guard,
    ShadowEngine, shadow_engine, ShadowOrderBook, ShadowFillSimulator,
    ShadowExecutionRouter, ShadowMarketReplay, ReplaySession
)
from backend.shadow_trading.shadow_latency_model import ShadowLatencyModel
from backend.shadow_trading.shadow_slippage_model import ShadowSlippageModel
from backend.shadow_trading.shadow_position_tracker import ShadowPositionTracker
from backend.shadow_trading.shadow_pnl_engine import ShadowPnLEngine
from backend.shadow_trading.shadow_governance import ShadowGovernance

# ---------------------------------------------------------
# 1. Safety Guard Tests (5 tests)
# ---------------------------------------------------------
def test_shadow_safety_guard_blocks_live_order():
    guard = ShadowSafetyGuard(mode=TradingMode.SHADOW)
    with pytest.raises(ShadowTradingViolation) as exc_info:
        guard.assert_shadow_safety("Live Order Submission")
    assert "strictly FORBIDDEN" in str(exc_info.value)

def test_shadow_safety_guard_blocks_ccxt_create_order():
    guard = ShadowSafetyGuard(mode=TradingMode.SHADOW)
    with pytest.raises(ShadowTradingViolation):
        guard.block_ccxt_create_order("BTC/USDT", "BUY", 1.0)

def test_shadow_safety_guard_blocks_withdrawal():
    guard = ShadowSafetyGuard(mode=TradingMode.SHADOW)
    with pytest.raises(ShadowTradingViolation):
        guard.block_withdrawal("USDT", 1000.0)

def test_shadow_safety_guard_blocks_leverage_change():
    guard = ShadowSafetyGuard(mode=TradingMode.SHADOW)
    with pytest.raises(ShadowTradingViolation):
        guard.block_leverage_change("BTC/USDT", 20)

def test_shadow_safety_guard_blocks_authenticated_ws():
    guard = ShadowSafetyGuard(mode=TradingMode.SHADOW)
    with pytest.raises(ShadowTradingViolation):
        guard.block_authenticated_ws()

# ---------------------------------------------------------
# 2. Orderbook & Market Data Feed Tests (4 tests)
# ---------------------------------------------------------
def test_shadow_orderbook_snapshot():
    ob = ShadowOrderBook()
    snapshot = ob.get_orderbook("BTC/USDT", current_price=50000.0)
    assert snapshot.symbol == "BTC/USDT"
    assert snapshot.best_ask > snapshot.best_bid
    assert len(snapshot.bids) == 10
    assert len(snapshot.asks) == 10

def test_shadow_orderbook_spread_calculation():
    ob = ShadowOrderBook()
    snapshot = ob.get_orderbook("ETH/USDT", current_price=3000.0)
    assert snapshot.spread_bps > 0.0
    assert snapshot.spread_usd == pytest.approx(snapshot.best_ask - snapshot.best_bid, 0.001)

def test_shadow_orderbook_depth_accumulation():
    ob = ShadowOrderBook()
    snapshot = ob.get_orderbook("SOL/USDT", current_price=150.0)
    assert snapshot.depth_usd > 0.0

def test_shadow_orderbook_dictionary_serialization():
    ob = ShadowOrderBook()
    snap_dict = ob.get_orderbook("BTC/USDT", 50000.0).to_dict()
    assert "symbol" in snap_dict
    assert "feed_status" in snap_dict
    assert snap_dict["feed_status"] == "LIVE"

# ---------------------------------------------------------
# 3. Slippage & Latency Model Tests (4 tests)
# ---------------------------------------------------------
def test_shadow_slippage_model_buy():
    model = ShadowSlippageModel()
    res = model.calculate_slippage("BTC/USDT", "BUY", 1.0, 50000.0)
    assert res.simulated_execution_price > res.expected_price
    assert res.slippage_bps > 0.0

def test_shadow_slippage_model_sell():
    model = ShadowSlippageModel()
    res = model.calculate_slippage("BTC/USDT", "SELL", 1.0, 50000.0)
    assert res.simulated_execution_price < res.expected_price

def test_shadow_latency_model_excellent_rating():
    model = ShadowLatencyModel()
    res = model.simulate_latency(base_network_ms=5.0, base_matching_ms=2.0, base_routing_ms=2.0, base_decision_ms=2.0)
    assert res.total_latency_ms < 20.0
    assert res.rating == "EXCELLENT"

def test_shadow_latency_model_degraded_rating():
    model = ShadowLatencyModel()
    res = model.simulate_latency(base_network_ms=50.0, base_matching_ms=30.0, base_routing_ms=20.0, base_decision_ms=10.0)
    assert res.total_latency_ms > 100.0
    assert res.rating == "DEGRADED"

# ---------------------------------------------------------
# 4. Fill Simulator & Queue Priority Tests (4 tests)
# ---------------------------------------------------------
def test_shadow_fill_simulator_market_order():
    sim = ShadowFillSimulator()
    fill = sim.simulate_fill("ORD-1", "BTC/USDT", "BUY", 0.5, "MARKET", 50000.0)
    assert fill.filled_qty == 0.5
    assert fill.execution_price > 0.0
    assert fill.fee_usd > 0.0

def test_shadow_fill_simulator_partial_fill_handling():
    sim = ShadowFillSimulator()
    fill = sim.simulate_fill("ORD-2", "BTC/USDT", "BUY", 100.0, "MARKET", 50000.0)
    assert fill.filled_qty > 0.0
    assert fill.remaining_qty >= 0.0

def test_shadow_fill_simulator_limit_order():
    sim = ShadowFillSimulator()
    fill = sim.simulate_fill("ORD-3", "ETH/USDT", "BUY", 2.0, "LIMIT", 3000.0)
    assert fill.symbol == "ETH/USDT"
    assert fill.execution_price > 0.0

def test_shadow_fill_simulator_latency_attachment():
    sim = ShadowFillSimulator()
    fill = sim.simulate_fill("ORD-4", "SOL/USDT", "SELL", 10.0, "MARKET", 150.0)
    assert fill.latency_ms > 0.0
    assert fill.latency_rating in ["EXCELLENT", "GOOD", "ACCEPTABLE", "DEGRADED"]

# ---------------------------------------------------------
# 5. Position Tracker & PnL Engine Tests (4 tests)
# ---------------------------------------------------------
def test_shadow_position_tracker_new_position():
    tracker = ShadowPositionTracker()
    sim = ShadowFillSimulator()
    fill = sim.simulate_fill("ORD-5", "BTC/USDT", "BUY", 1.0, "MARKET", 50000.0)
    pos = tracker.update_position_from_fill(fill)
    assert pos.symbol == "BTC/USDT"
    assert pos.quantity == 1.0

def test_shadow_position_tracker_average_entry():
    tracker = ShadowPositionTracker()
    sim = ShadowFillSimulator()
    f1 = sim.simulate_fill("ORD-6A", "BTC/USDT", "BUY", 1.0, "MARKET", 50000.0)
    tracker.update_position_from_fill(f1)
    f2 = sim.simulate_fill("ORD-6B", "BTC/USDT", "BUY", 1.0, "MARKET", 60000.0)
    pos = tracker.update_position_from_fill(f2)
    assert pos.quantity == 2.0
    assert pos.average_entry_price > 50000.0

def test_shadow_pnl_engine_computation():
    engine = ShadowPnLEngine()
    tracker = ShadowPositionTracker()
    sim = ShadowFillSimulator()
    f = sim.simulate_fill("ORD-7", "BTC/USDT", "BUY", 1.0, "MARKET", 50000.0)
    pos = tracker.update_position_from_fill(f)
    analytics = engine.compute_pnl_analytics([pos], [f])
    assert analytics.fill_quality_score > 0.0
    assert analytics.implementation_shortfall_bps > 0.0

def test_shadow_pnl_engine_serialization():
    engine = ShadowPnLEngine()
    analytics = engine.compute_pnl_analytics([], []).to_dict()
    assert "gross_pnl_usd" in analytics
    assert "fill_quality_score" in analytics

# ---------------------------------------------------------
# 6. Replay, Governance & Engine Integration Tests (4 tests)
# ---------------------------------------------------------
def test_shadow_market_replay_session():
    replay = ShadowMarketReplay()
    session = replay.start_replay("BTC/USDT", playback_speed=10)
    assert session.status == "RUNNING"
    assert session.playback_speed == 10
    stopped = replay.stop_replay(session.session_id)
    assert stopped.status == "COMPLETED"

def test_shadow_governance_approval_pass():
    gov = ShadowGovernance()
    res = gov.validate_shadow_approval(portfolio_heat_utilization_pct=20.0, kill_switch_state="NORMAL", paper_readiness_score=97.4)
    assert res.is_approved is True
    assert res.status == "SHADOW_APPROVED"

def test_shadow_governance_approval_fail_kill_switch():
    gov = ShadowGovernance()
    res = gov.validate_shadow_approval(portfolio_heat_utilization_pct=20.0, kill_switch_state="HALTED", paper_readiness_score=97.4)
    assert res.is_approved is False
    assert res.status == "SHADOW_HALTED"

def test_shadow_engine_orchestration_workflow():
    engine = ShadowEngine()
    start_res = engine.start_shadow_session()
    assert start_res["status"] == "success"
    exec_res = engine.router.execute_shadow_order("BTC/USDT", "BUY", 0.5, "MARKET", 50000.0)
    assert exec_res["status"] == "success"
    assert exec_res["mode"] == "SHADOW"
    stop_res = engine.stop_shadow_session()
    assert stop_res["session_status"] == "IDLE"
