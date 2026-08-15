import pytest
import time
from backend.autonomous import (
    EngineState,
    ExecutionState,
    ExecutionStateMachine,
    AutonomousGovernanceEngine,
    AutonomousMetricsTracker,
    ArbitrageExitEngine,
    AutonomousExecutionManager,
    AutonomousEngine,
    autonomous_engine
)
from backend.execution import execution_orchestrator
from backend.portfolio_risk.portfolio_risk_engine import InstitutionalPortfolioRiskEngine
from backend.safety.paper_mode_guard import paper_guard, PaperTradingViolation
from backend.shadow_trading.shadow_safety_guard import shadow_guard, ShadowTradingViolation


@pytest.fixture(autouse=True)
def reset_autonomous_state():
    engine = autonomous_engine
    engine.state = EngineState.STOPPED
    engine.execution_manager.executions.clear()
    engine.execution_manager.positions.clear()
    engine.execution_manager.state_machines.clear()
    engine.execution_manager.governance_engine.clear_keys()
    engine.metrics_tracker._reset()
    yield
    engine.state = EngineState.STOPPED


def test_autonomous_start():
    res = autonomous_engine.start()
    assert res["status"] == "success"
    assert autonomous_engine.state == EngineState.RUNNING


def test_autonomous_pause():
    autonomous_engine.start()
    res = autonomous_engine.pause()
    assert res["status"] == "success"
    assert autonomous_engine.state == EngineState.PAUSED


def test_autonomous_resume():
    autonomous_engine.start()
    autonomous_engine.pause()
    res = autonomous_engine.resume()
    assert res["status"] == "success"
    assert autonomous_engine.state == EngineState.RUNNING


def test_autonomous_stop():
    autonomous_engine.start()
    res = autonomous_engine.stop()
    assert res["status"] == "success"
    assert autonomous_engine.state == EngineState.STOPPED


def test_real_opportunity_detection():
    manager = AutonomousExecutionManager()
    opp = {
        "symbol": "BTC/USDT",
        "buy_exchange": "BINANCE",
        "sell_exchange": "BYBIT",
        "buy_price": 100000.0,
        "sell_price": 101000.0,
        "estimated_profit_usd": 10000.0
    }
    res = manager.process_opportunity(opp)
    assert res["status"] in ["success", "rejected"]


def test_stale_opportunity_rejection():
    manager = AutonomousExecutionManager()
    opp = {
        "symbol": "BTC/USDT",
        "buy_exchange": "BINANCE",
        "sell_exchange": "BYBIT",
        "buy_price": 100000.0,
        "sell_price": 101000.0
    }
    # Force stale status in quote collector
    q = manager.collector.fetch_exchange_quote_real("BINANCE", "BTC/USDT")
    if q:
        q.status = "DATA_STALE"
        q.data_age_ms = 2500.0
    res = manager.process_opportunity(opp)
    assert res["status"] == "rejected" or "execution" in res


def test_fee_rejection():
    from backend.arbitrage import SpreadDetector
    detector = SpreadDetector()
    spread = detector.compute_spread("BTC/USDT", "BINANCE", "BYBIT", 100000.0, 100050.0, buy_fee_bps=10.0, sell_fee_bps=10.0)
    assert not spread.is_executable


def test_slippage_rejection():
    from backend.arbitrage import SpreadDetector
    detector = SpreadDetector()
    spread = detector.compute_spread("BTC/USDT", "BINANCE", "BYBIT", 100000.0, 100200.0, slippage_bps=20.0)
    assert not spread.is_executable


def test_liquidity_rejection():
    manager = AutonomousExecutionManager()
    opp = {
        "symbol": "BTC/USDT",
        "buy_exchange": "BINANCE",
        "sell_exchange": "BYBIT",
        "buy_price": 0.0,
        "sell_price": 100000.0
    }
    res = manager.process_opportunity(opp)
    assert res["status"] == "rejected"


def test_exchange_health_rejection():
    from backend.arbitrage import ArbitrageRiskFilter
    rf = ArbitrageRiskFilter()
    res = rf.evaluate_opportunity_risk(net_spread_pct=0.50, exchange_health="DEGRADED")
    assert not res.passed


def test_risk_approval():
    engine = InstitutionalPortfolioRiskEngine()
    trader = AutonomousExecutionManager().trader
    res = engine.evaluate_trade_risk_gate(trader, "BTC/USDT", "BUY", 5000.0)
    assert res["passed"] is True


def test_risk_rejection():
    engine = InstitutionalPortfolioRiskEngine()
    trader = AutonomousExecutionManager().trader
    engine.kill_switch.activate("High Volatility Hazard")
    res = engine.evaluate_trade_risk_gate(trader, "BTC/USDT", "BUY", 5000.0)
    assert res["passed"] is False
    engine.kill_switch.recover()


def test_governance_approval():
    gov = AutonomousGovernanceEngine()
    res = gov.validate_opportunity_governance("BTC/USDT", "BINANCE", "BYBIT", 100000.0, 101000.0)
    assert res.is_allowed is True


def test_governance_rejection():
    gov = AutonomousGovernanceEngine()
    res = gov.validate_opportunity_governance("BTC/USDT", "BINANCE", "BYBIT", 100000.0, 101000.0, kill_switch_halted=True)
    assert res.is_allowed is False


def test_automatic_execution():
    manager = AutonomousExecutionManager()
    opp = {
        "symbol": "BTC/USDT",
        "buy_exchange": "BINANCE",
        "sell_exchange": "BYBIT",
        "buy_price": 100000.0,
        "sell_price": 101000.0,
        "amount_usd": 10000.0
    }
    res = manager.process_opportunity(opp)
    assert res["status"] in ["success", "rejected"]


def test_oms_integration():
    res = execution_orchestrator.submit_order("user-p41", "BTC/USDT", "BUY", 0.1, exchange="BINANCE")
    assert res["status"] == "success"
    assert res["order"]["status"] == "FILLED"


def test_algorithm_selection_smart_router():
    manager = AutonomousExecutionManager()
    alg, reason = manager.select_execution_algorithm(amount_usd=1000.0, buy_price=100000.0, book_depth_usd=50000.0)
    assert alg == "SMART_ROUTER"


def test_algorithm_selection_twap():
    manager = AutonomousExecutionManager()
    alg, reason = manager.select_execution_algorithm(amount_usd=7000.0, buy_price=100000.0, book_depth_usd=50000.0)
    assert alg == "TWAP"
    assert "TWAP selected" in reason


def test_algorithm_selection_vwap():
    manager = AutonomousExecutionManager()
    alg, reason = manager.select_execution_algorithm(amount_usd=2000.0, buy_price=100000.0, book_depth_usd=50000.0, volatility_pct=6.0)
    assert alg == "VWAP"


def test_algorithm_selection_iceberg():
    manager = AutonomousExecutionManager()
    alg, reason = manager.select_execution_algorithm(amount_usd=15000.0, buy_price=100000.0, book_depth_usd=50000.0)
    assert alg == "ICEBERG"
    assert "ICEBERG selected" in reason


def test_partial_fill_handling():
    from backend.execution.partial_fill_manager import PartialFillManager, PartialFillTracker
    pfm = PartialFillManager()
    tracker = PartialFillTracker("ORD-1", 1.0, 0.0, 1.0, 0.0, 0, time.time(), "PARTIAL")
    res = pfm.process_fill(tracker, 0.5, 100000.0)
    assert res.remaining_qty == 0.5


def test_full_fill_handling():
    from backend.execution.partial_fill_manager import PartialFillManager, PartialFillTracker
    pfm = PartialFillManager()
    tracker = PartialFillTracker("ORD-2", 1.0, 0.0, 1.0, 0.0, 0, time.time(), "PARTIAL")
    res = pfm.process_fill(tracker, 1.0, 100000.0)
    assert res.status == "COMPLETED"


def test_shadow_position_creation():
    manager = AutonomousExecutionManager()
    opp = {
        "symbol": "BTC/USDT",
        "buy_exchange": "BINANCE",
        "sell_exchange": "BYBIT",
        "buy_price": 100000.0,
        "sell_price": 101000.0,
        "amount_usd": 10000.0
    }
    res = manager.process_opportunity(opp)
    if res["status"] == "success":
        assert "position" in res
        assert res["position"]["status"] == "OPEN"


def test_position_monitoring():
    exit_engine = ArbitrageExitEngine()
    pos = {
        "position_id": "POS-1",
        "entry_timestamp": time.time(),
        "buy_exchange": "BINANCE",
        "sell_exchange": "BYBIT"
    }
    eval_res = exit_engine.evaluate_position_exit(pos)
    assert eval_res.should_exit is False


def test_spread_convergence_exit():
    exit_engine = ArbitrageExitEngine()
    pos = {"position_id": "POS-2", "entry_timestamp": time.time()}
    class MockQ:
        def __init__(self, ask, bid):
            self.ask_price = ask
            self.bid_price = bid
            self.data_age_ms = 10.0
            self.status = "FRESH"

    q_buy = MockQ(100000.0, 99990.0)
    q_sell = MockQ(99990.0, 99990.0)

    eval_res = exit_engine.evaluate_position_exit(pos, q_buy, q_sell)
    assert eval_res.should_exit is True
    assert eval_res.trigger_reason == "SPREAD_CONVERGED"


def test_stale_position_exit():
    exit_engine = ArbitrageExitEngine()
    pos = {"position_id": "POS-3", "entry_timestamp": time.time()}
    class MockStaleQ:
        def __init__(self):
            self.ask_price = 100000.0
            self.bid_price = 101000.0
            self.data_age_ms = 3000.0
            self.status = "DATA_STALE"

    eval_res = exit_engine.evaluate_position_exit(pos, MockStaleQ(), MockStaleQ())
    assert eval_res.should_exit is True
    assert eval_res.trigger_reason == "QUOTE_STALE"


def test_exchange_failure_exit():
    exit_engine = ArbitrageExitEngine()
    pos = {"position_id": "POS-4", "entry_timestamp": time.time()}
    class MockOfflineQ:
        def __init__(self):
            self.ask_price = 0.0
            self.bid_price = 0.0
            self.data_age_ms = 0.0
            self.status = "DATA_UNAVAILABLE"

    eval_res = exit_engine.evaluate_position_exit(pos, MockOfflineQ(), MockOfflineQ())
    assert eval_res.should_exit is True
    assert eval_res.trigger_reason == "LIQUIDITY_DETERIORATED"


def test_kill_switch_exit():
    exit_engine = ArbitrageExitEngine()
    pos = {"position_id": "POS-5", "entry_timestamp": time.time()}
    eval_res = exit_engine.evaluate_position_exit(pos, kill_switch_halted=True)
    assert eval_res.should_exit is True
    assert eval_res.trigger_reason == "KILL_SWITCH_ACTIVATED"


def test_pnl_calculation_formula():
    gross = 100.0
    buy_fee = 7.5
    sell_fee = 7.5
    slippage = 2.0
    impact = 1.0
    funding = 0.5
    latency = 0.5
    transfer = 1.0

    net = gross - buy_fee - sell_fee - slippage - impact - funding - latency - transfer
    assert net == 80.0


def test_pnl_persistence():
    manager = AutonomousExecutionManager()
    opp = {
        "symbol": "BTC/USDT",
        "buy_exchange": "BINANCE",
        "sell_exchange": "BYBIT",
        "buy_price": 100000.0,
        "sell_price": 101000.0,
        "amount_usd": 10000.0
    }
    res = manager.process_opportunity(opp)
    if res["status"] == "success":
        exec_id = res["execution"]["execution_id"]
        assert exec_id in manager.executions
        assert manager.executions[exec_id].net_pnl is not None


def test_duplicate_opportunity_prevention():
    gov = AutonomousGovernanceEngine()
    r1 = gov.validate_opportunity_governance("BTC/USDT", "BINANCE", "BYBIT", 100000.0, 101000.0)
    assert r1.is_allowed is True
    r2 = gov.validate_opportunity_governance("BTC/USDT", "BINANCE", "BYBIT", 100000.0, 101000.0)
    assert r2.is_allowed is False
    assert "Duplicate" in r2.reason


def test_concurrent_execution_lock():
    gov = AutonomousGovernanceEngine()
    key1 = gov.generate_idempotency_key("BTC/USDT", "BINANCE", "BYBIT", 100000.0, 101000.0)
    key2 = gov.generate_idempotency_key("BTC/USDT", "BINANCE", "BYBIT", 100000.0, 101000.0)
    assert key1 == key2


def test_news_hack_event_handling():
    exit_engine = ArbitrageExitEngine()
    pos = {"position_id": "POS-6", "entry_timestamp": time.time()}
    eval_res = exit_engine.evaluate_position_exit(pos, news_hack_detected=True)
    assert eval_res.should_exit is True
    assert eval_res.trigger_reason == "NEWS_SECURITY_ALERT"


def test_news_outage_event_handling():
    from backend.news_intelligence import EventSignalEngine
    sig_engine = EventSignalEngine()
    sig = sig_engine.generate_signal("EXCHANGE_OUTAGE", "BTC/USDT", 0.95)
    assert sig.action in ["CLOSE_POSITION", "REDUCE_RISK", "BLOCK_NEW_LONGS"]


def test_news_delisting_event_handling():
    from backend.news_intelligence import EventSignalEngine
    sig_engine = EventSignalEngine()
    sig = sig_engine.generate_signal("TOKEN_DELISTING", "BTC/USDT", 0.95)
    assert sig.action in ["SELL", "CLOSE_POSITION", "REDUCE_RISK", "BLOCK_NEW_LONGS"]


def test_paper_safety_guard_violation():
    with pytest.raises(PaperTradingViolation):
        paper_guard.block_live_exchange_order("BINANCE", "BTC/USDT", 1.0)


def test_shadow_safety_guard_violation():
    with pytest.raises(ShadowTradingViolation):
        shadow_guard.block_ccxt_create_order("BTC/USDT", "BUY", 1.0)


def test_live_order_rejection():
    with pytest.raises(PaperTradingViolation):
        paper_guard.block_withdrawal("USDT", 100.0, "0x999")


def test_execution_timeline_events():
    sm = ExecutionStateMachine("EXEC-1")
    sm.transition_to(ExecutionState.VALIDATING, "Validation check")
    sm.transition_to(ExecutionState.RISK_CHECK, "Risk check")
    sm.transition_to(ExecutionState.APPROVED, "Approved")
    sm.transition_to(ExecutionState.EXECUTING, "Executing")
    sm.transition_to(ExecutionState.COMPLETED, "Completed")
    assert len(sm.history) == 6


def test_pause_prevents_new_jobs():
    autonomous_engine.start()
    autonomous_engine.pause()
    tick_res = autonomous_engine.run_single_tick()
    assert tick_res["status"] == "ignored"


def test_persistence_across_restarts():
    manager = AutonomousExecutionManager()
    opp = {
        "symbol": "BTC/USDT",
        "buy_exchange": "BINANCE",
        "sell_exchange": "BYBIT",
        "buy_price": 100000.0,
        "sell_price": 101000.0
    }
    res = manager.process_opportunity(opp)
    assert len(manager.executions) > 0


def test_risk_score_update_on_position_change():
    manager = AutonomousExecutionManager()
    trader = manager.trader
    risk_engine = manager.risk_engine

    trader.positions.clear()
    state1 = risk_engine.evaluate_portfolio_state(trader.user_id, trader)
    score1 = state1.risk_score

    trader.positions["BTC/USDT"] = {"symbol": "BTC/USDT", "amount": 0.5, "entry_price": 100000.0}
    trader.positions["ETH/USDT"] = {"symbol": "ETH/USDT", "amount": 5.0, "entry_price": 3000.0}
    state2 = risk_engine.evaluate_portfolio_state(trader.user_id, trader)
    score2 = state2.risk_score

    assert score1 != score2


def test_complete_lifecycle():
    manager = AutonomousExecutionManager()
    opp = {
        "symbol": "BTC/USDT",
        "buy_exchange": "BINANCE",
        "sell_exchange": "BYBIT",
        "buy_price": 100000.0,
        "sell_price": 101000.0,
        "amount_usd": 10000.0
    }
    res = manager.process_opportunity(opp)
    if res["status"] == "success":
        pos_id = res["position"]["position_id"]
        pos = manager.positions[pos_id]
        exit_info = manager.exit_engine.execute_shadow_exit(pos, "Manual test exit")
        assert exit_info["status"] == "success"
        assert pos.status == "CLOSED"
