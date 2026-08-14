import pytest
from backend.portfolio_risk.user_risk_profile import UserRiskProfileManager

def test_user_risk_profile_presets():
    mgr = UserRiskProfileManager()

    cons = mgr.get_profile("CONSERVATIVE")
    assert cons.max_leverage == 2
    assert cons.risk_multiplier == 0.60

    agg = mgr.get_profile("AGGRESSIVE")
    assert agg.max_leverage == 10
    assert agg.risk_multiplier == 1.40
