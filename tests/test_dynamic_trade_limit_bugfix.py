import pytest
from backend.portfolio_risk.dynamic_trade_limit import DynamicTradeLimitEngine
from backend.portfolio_risk.user_risk_profile import UserRiskProfileManager
from backend.portfolio_risk.portfolio_risk_engine import InstitutionalPortfolioRiskEngine

def test_missing_profile_returns_non_zero_defaults():
    mgr = UserRiskProfileManager()
    prof = mgr.get_profile("UNKNOWN_PROFILE")
    assert prof.max_concurrent_trades == 10
    assert prof.max_capital_per_trade_pct == 10.0
    assert prof.daily_loss_limit_pct == 5.0

def test_dynamic_trade_limit_never_zero_on_normal():
    engine = DynamicTradeLimitEngine()
    res = engine.compute_effective_limit(
        user_configured_max_positions=0,  # Missing/invalid
        currently_open_positions=2,
        portfolio_heat_status="NORMAL",
        drawdown_pct=0.0
    )
    assert res.configured_max_positions == 10
    assert res.dynamic_risk_limit == 10
    assert res.effective_max_positions == 10
    assert res.available_trade_slots == 8
    assert res.can_open_new_trade is True

def test_dynamic_trade_limit_zero_only_when_halted():
    engine = DynamicTradeLimitEngine()
    res = engine.compute_effective_limit(
        user_configured_max_positions=10,
        currently_open_positions=0,
        is_kill_switch_halted=True
    )
    assert res.effective_max_positions == 0
    assert res.available_trade_slots == 0
    assert res.can_open_new_trade is False
    assert res.constraining_factor == "KILL_SWITCH_HALTED"

def test_critical_heat_caps_limit_without_zeroing():
    engine = DynamicTradeLimitEngine()
    res = engine.compute_effective_limit(
        user_configured_max_positions=10,
        currently_open_positions=1,
        portfolio_heat_status="CRITICAL"
    )
    assert res.effective_max_positions == 2  # 20% of 10
    assert res.available_trade_slots == 1
    assert res.can_open_new_trade is True
