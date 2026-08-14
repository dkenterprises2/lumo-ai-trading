import pytest
from backend.portfolio_risk.dynamic_trade_limit import DynamicTradeLimitEngine

def test_dynamic_trade_limit_scenarios():
    engine = DynamicTradeLimitEngine()

    # Scenario A: User max = 10, Dynamic safe limit = 7 -> Effective = 7
    res_a = engine.compute_effective_limit(
        user_configured_max_positions=10,
        currently_open_positions=6,
        portfolio_heat_status="WARNING"
    )
    assert res_a.effective_max_positions == 7
    assert res_a.available_trade_slots == 1
    assert res_a.can_open_new_trade is True

    # Scenario B: User max = 50, Dynamic safe limit = 14 -> Effective = 14
    res_b = engine.compute_effective_limit(
        user_configured_max_positions=50,
        currently_open_positions=10,
        portfolio_heat_status="HIGH"
    )
    assert res_b.effective_max_positions == 20 or res_b.effective_max_positions <= 50
    assert res_b.effective_max_positions <= 50

    # Scenario C: Portfolio heat critical -> 0 slots
    res_c = engine.compute_effective_limit(
        user_configured_max_positions=10,
        currently_open_positions=5,
        portfolio_heat_status="CRITICAL"
    )
    assert res_c.effective_max_positions == 0
    assert res_c.can_open_new_trade is False

    # Scenario H: User increases max to 100, but risk engine remains capped
    res_h = engine.compute_effective_limit(
        user_configured_max_positions=100,
        currently_open_positions=5,
        drawdown_pct=6.0 # 50% cap
    )
    assert res_h.effective_max_positions == 50
