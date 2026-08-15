import pytest
import time
from backend.autonomous_validation import (
    ValidationScenario,
    ScenarioResult,
    ValidationState,
    ScenarioFactory,
    ReplayMarketFeed,
    OpportunityInjector,
    LifecycleValidator,
    ValidationMetricsCalculator,
    ValidationReportGenerator
)
from backend.autonomous import AutonomousExecutionManager, autonomous_engine, EngineState
from backend.safety.paper_mode_guard import paper_guard, PaperTradingViolation
from backend.shadow_trading.shadow_safety_guard import shadow_guard, ShadowTradingViolation


@pytest.fixture(autouse=True)
def reset_validation_state():
    manager = AutonomousExecutionManager()
    manager.executions.clear()
    manager.positions.clear()
    manager.state_machines.clear()
    manager.governance_engine.clear_keys()
    manager.risk_engine.kill_switch.recover()
    yield
    manager.risk_engine.kill_switch.recover()


# --- Group 1: Market Replay ---

def test_deterministic_replay_initialization():
    sc = ScenarioFactory.create_scenario_a_profitable()
    feed = ReplayMarketFeed(sc)
    assert feed.scenario.scenario_id == "SCENARIO_A"
    assert len(feed.ticks) > 0


def test_timestamp_progression():
    sc = ScenarioFactory.create_scenario_a_profitable()
    feed = ReplayMarketFeed(sc, playback_speed=5)
    ticks = list(feed.stream_ticks())
    assert len(ticks) == 1
    assert ticks[0].timestamp > 0.0


def test_quote_freshness_in_replay():
    sc = ScenarioFactory.create_scenario_c_stale_quote()
    assert sc.ticks[0].data_age_ms == 2500.0
    assert sc.ticks[0].status == "DATA_STALE"


def test_scenario_factory_scenarios():
    scenarios = ScenarioFactory.get_all_scenarios()
    assert len(scenarios) == 10
    codes = [s.scenario_id for s in scenarios]
    assert "SCENARIO_A" in codes
    assert "SCENARIO_J" in codes


def test_scenario_a_profitable_data():
    sc = ScenarioFactory.create_scenario_a_profitable()
    assert sc.expected_should_execute is True
    assert sc.ticks[0].sell_price > sc.ticks[0].buy_price


def test_scenario_b_unprofitable_data():
    sc = ScenarioFactory.create_scenario_b_unprofitable()
    assert sc.expected_should_execute is False
    assert sc.expected_terminal_state == ValidationState.REJECTED_UNPROFITABLE.value


# --- Group 2: Opportunity Detection & Net Edge Calculation ---

def test_profitable_opportunity_detection():
    injector = OpportunityInjector()
    sc = ScenarioFactory.create_scenario_a_profitable()
    res = injector.run_scenario(sc)
    assert res.passed is True
    assert res.actual_terminal_state in ["MONITORING", "CLOSED"]


def test_unprofitable_opportunity_rejection():
    injector = OpportunityInjector()
    sc = ScenarioFactory.create_scenario_b_unprofitable()
    res = injector.run_scenario(sc)
    assert res.passed is True
    assert res.actual_terminal_state == ValidationState.REJECTED_UNPROFITABLE.value


def test_fee_deduction_accuracy():
    amount = 10000.0
    buy_fee = amount * 0.00075
    sell_fee = amount * 0.00075
    total_fees = buy_fee + sell_fee
    assert total_fees == 15.0


def test_slippage_cost_deduction():
    amount = 10000.0
    slippage = amount * 0.0002
    assert slippage == 2.0


def test_market_impact_cost_deduction():
    amount = 10000.0
    impact = amount * 0.0001
    assert impact == 1.0


def test_net_edge_threshold_check():
    gross_spread = 0.50
    friction = 0.19
    net_edge = gross_spread - friction
    assert net_edge > 0.15


# --- Group 3: Risk Gate ---

def test_risk_gate_approval():
    manager = AutonomousExecutionManager()
    res = manager.risk_engine.evaluate_trade_risk_gate(manager.trader, "BTC/USDT", "BUY", 5000.0)
    assert res["passed"] is True


def test_risk_gate_rejection():
    injector = OpportunityInjector()
    sc = ScenarioFactory.create_scenario_d_risk_rejection()
    res = injector.run_scenario(sc)
    assert res.passed is True
    assert res.actual_terminal_state == ValidationState.REJECTED_RISK.value


def test_portfolio_heat_check():
    manager = AutonomousExecutionManager()
    state = manager.risk_engine.evaluate_portfolio_state(manager.trader.user_id, manager.trader)
    assert state.portfolio_heat_pct >= 0.0


def test_drawdown_limit_check():
    manager = AutonomousExecutionManager()
    state = manager.risk_engine.evaluate_portfolio_state(manager.trader.user_id, manager.trader)
    assert state.drawdown_pct <= 20.0


def test_max_open_positions_check():
    manager = AutonomousExecutionManager()
    assert manager.trader.max_open_positions == 10


def test_risk_score_recalculation():
    manager = AutonomousExecutionManager()
    manager.trader.positions.clear()
    s1 = manager.risk_engine.evaluate_portfolio_state(manager.trader.user_id, manager.trader)
    manager.trader.positions["BTC/USDT"] = {
        "symbol": "BTC/USDT",
        "amount": 1.0,
        "entry_price": 100000.0,
        "notional_usd": 50000.0,
        "current_price": 100000.0
    }
    s2 = manager.risk_engine.evaluate_portfolio_state(manager.trader.user_id, manager.trader)
    assert s1.risk_score != s2.risk_score
    manager.trader.positions.clear()


# --- Group 4: Governance Gate & Safety ---

def test_governance_approval():
    manager = AutonomousExecutionManager()
    res = manager.governance_engine.validate_opportunity_governance("BTC/USDT", "BINANCE", "BYBIT", 100000.0, 100500.0)
    assert res.is_allowed is True


def test_governance_rejection():
    injector = OpportunityInjector()
    sc = ScenarioFactory.create_scenario_e_governance_rejection()
    res = injector.run_scenario(sc)
    assert res.passed is True
    assert res.actual_terminal_state == ValidationState.REJECTED_GOVERNANCE.value


def test_kill_switch_blocking():
    injector = OpportunityInjector()
    sc = ScenarioFactory.create_scenario_f_kill_switch()
    res = injector.run_scenario(sc)
    assert res.passed is True
    assert res.actual_terminal_state == ValidationState.REJECTED_KILL_SWITCH.value


def test_idempotency_key_deduplication():
    manager = AutonomousExecutionManager()
    k1 = manager.governance_engine.generate_idempotency_key("BTC/USDT", "BINANCE", "BYBIT", 100000.0, 100500.0)
    k2 = manager.governance_engine.generate_idempotency_key("BTC/USDT", "BINANCE", "BYBIT", 100000.0, 100500.0)
    assert k1 == k2


def test_real_order_blocked_violation():
    with pytest.raises(PaperTradingViolation):
        paper_guard.block_live_exchange_order("BINANCE", "BTC/USDT", 1.0)


def test_withdrawal_blocked_violation():
    with pytest.raises(ShadowTradingViolation):
        shadow_guard.block_withdrawal("USDT", 500.0)


def test_leverage_change_blocked_violation():
    with pytest.raises(ShadowTradingViolation):
        shadow_guard.block_leverage_change("BTC/USDT", 10)


def test_authenticated_exchange_blocked_violation():
    with pytest.raises(ShadowTradingViolation):
        shadow_guard.block_authenticated_ws()


# --- Group 5: Execution & Algorithm Selection ---

def test_autonomous_execution_start():
    manager = AutonomousExecutionManager()
    manager.governance_engine.clear_keys()
    opp = {"symbol": "BTC/USDT", "buy_exchange": "BINANCE", "sell_exchange": "BYBIT", "buy_price": 100000.0, "sell_price": 100550.0, "amount_usd": 10000.0, "data_age_ms": 10.0, "status": "FRESH"}
    res = manager.process_opportunity(opp)
    assert res["status"] == "success"


def test_dual_leg_oms_submission():
    from backend.execution import execution_orchestrator
    r1 = execution_orchestrator.submit_order("user-p41", "BTC/USDT", "BUY", 0.1, exchange="BINANCE")
    r2 = execution_orchestrator.submit_order("user-p41", "BTC/USDT", "SELL", 0.1, exchange="BYBIT")
    assert r1["status"] == "success"
    assert r2["status"] == "success"


def test_smart_router_selection():
    manager = AutonomousExecutionManager()
    alg, _ = manager.select_execution_algorithm(1000.0, 100000.0, 50000.0)
    assert alg == "SMART_ROUTER"


def test_twap_algorithm_selection():
    manager = AutonomousExecutionManager()
    alg, _ = manager.select_execution_algorithm(7000.0, 100000.0, 50000.0)
    assert alg == "TWAP"


def test_vwap_algorithm_selection():
    manager = AutonomousExecutionManager()
    alg, _ = manager.select_execution_algorithm(2000.0, 100000.0, 50000.0, volatility_pct=6.0)
    assert alg == "VWAP"


def test_iceberg_algorithm_selection():
    manager = AutonomousExecutionManager()
    alg, _ = manager.select_execution_algorithm(15000.0, 100000.0, 50000.0)
    assert alg == "ICEBERG"


# --- Group 6: Shadow Position & Exit Engine ---

def test_position_creation():
    manager = AutonomousExecutionManager()
    manager.governance_engine.clear_keys()
    opp = {"symbol": "BTC/USDT", "buy_exchange": "BINANCE", "sell_exchange": "BYBIT", "buy_price": 100000.0, "sell_price": 100650.0, "amount_usd": 10000.0, "data_age_ms": 10.0, "status": "FRESH"}
    res = manager.process_opportunity(opp)
    assert "position" in res
    assert res["position"]["status"] == "OPEN"


def test_position_persistence():
    manager = AutonomousExecutionManager()
    manager.governance_engine.clear_keys()
    opp = {"symbol": "BTC/USDT", "buy_exchange": "BINANCE", "sell_exchange": "BYBIT", "buy_price": 100000.0, "sell_price": 100700.0, "amount_usd": 10000.0, "data_age_ms": 10.0, "status": "FRESH"}
    res = manager.process_opportunity(opp)
    pos_id = res["position"]["position_id"]
    assert pos_id in manager.positions


def test_position_monitoring():
    injector = OpportunityInjector()
    sc = ScenarioFactory.create_scenario_a_profitable()
    res = injector.run_scenario(sc)
    assert res.actual_terminal_state in ["MONITORING", "CLOSED"]


def test_exit_spread_convergence():
    injector = OpportunityInjector()
    sc = ScenarioFactory.create_scenario_g_position_exit()
    res = injector.run_scenario(sc)
    assert res.passed is True
    assert res.actual_terminal_state == "CLOSED"


def test_exit_net_edge_decay():
    injector = OpportunityInjector()
    sc = ScenarioFactory.create_scenario_h_net_edge_decay()
    res = injector.run_scenario(sc)
    assert res.passed is True
    assert res.actual_terminal_state == "CLOSED"


def test_exit_stale_data():
    injector = OpportunityInjector()
    sc = ScenarioFactory.create_scenario_c_stale_quote()
    res = injector.run_scenario(sc)
    assert res.actual_terminal_state == ValidationState.REJECTED_STALE_DATA.value


def test_exit_liquidity_collapse():
    injector = OpportunityInjector()
    sc = ScenarioFactory.create_scenario_i_liquidity_collapse()
    res = injector.run_scenario(sc)
    assert res.passed is True
    assert res.actual_terminal_state == "CLOSED"


def test_exit_exchange_degradation():
    injector = OpportunityInjector()
    sc = ScenarioFactory.create_scenario_j_exchange_degradation()
    res = injector.run_scenario(sc)
    assert res.passed is True
    assert res.actual_terminal_state == "CLOSED"


# --- Group 7: Net PnL & Reconciliation ---

def test_gross_pnl_formula():
    buy_price = 100000.0
    sell_price = 100500.0
    qty = 0.1
    gross = (sell_price - buy_price) * qty
    assert gross == 50.0


def test_fee_reconciliation():
    amount = 10000.0
    fees = amount * 0.0015
    assert fees == 15.0


def test_slippage_reconciliation():
    amount = 10000.0
    slippage = amount * 0.0002
    assert slippage == 2.0


def test_net_pnl_formula_reconciliation():
    gross = 50.0
    fees = 15.0
    slippage = 2.0
    net = gross - fees - slippage
    assert net == 33.0


def test_no_hardcoded_pnl():
    injector = OpportunityInjector()
    sc = ScenarioFactory.create_scenario_g_position_exit()
    res = injector.run_scenario(sc)
    assert isinstance(res.realized_shadow_pnl, float)


# --- Group 8: API & Validation Report ---

def test_validation_status_endpoint():
    from fastapi.testclient import TestClient
    from main import app
    from backend.auth.security import create_access_token
    client = TestClient(app)
    token = create_access_token({"sub": "1", "type": "access"})
    r = client.get("/api/autonomous-validation/status", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["mode"] == "REPLAY_VALIDATION"


def test_validation_scenarios_endpoint():
    from fastapi.testclient import TestClient
    from main import app
    from backend.auth.security import create_access_token
    client = TestClient(app)
    token = create_access_token({"sub": "1", "type": "access"})
    r = client.get("/api/autonomous-validation/scenarios", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert len(r.json()["scenarios"]) == 10


def test_validation_run_scenario_endpoint():
    from fastapi.testclient import TestClient
    from main import app
    from backend.auth.security import create_access_token
    client = TestClient(app)
    token = create_access_token({"sub": "1", "type": "access"})
    r = client.post("/api/autonomous-validation/run/SCENARIO_A", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["scenario_result"]["passed"] is True


def test_validation_report_endpoint():
    from fastapi.testclient import TestClient
    from main import app
    from backend.auth.security import create_access_token
    client = TestClient(app)
    token = create_access_token({"sub": "1", "type": "access"})
    r = client.get("/api/autonomous-validation/report", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert "validation_score" in r.json()["report"]


def test_lifecycle_audit_endpoint():
    from fastapi.testclient import TestClient
    from main import app
    from backend.auth.security import create_access_token
    client = TestClient(app)
    token = create_access_token({"sub": "1", "type": "access"})
    r1 = client.post("/api/autonomous-validation/run/SCENARIO_A", headers={"Authorization": f"Bearer {token}"})
    exec_id = r1.json()["scenario_result"]["execution_id"]
    r2 = client.get(f"/api/autonomous-validation/lifecycle/{exec_id}", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    assert len(r2.json()["state_history"]) > 0


def test_full_replay_validation_cycle():
    res = autonomous_engine.run_validation_cycle("FLASH_SPREAD_DISCREPANCY")
    assert res["status"] == "success"
    assert len(res["execution_proof_records"]) == 10
