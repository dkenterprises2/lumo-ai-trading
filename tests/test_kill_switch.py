import pytest
from backend.portfolio_risk.kill_switch import PortfolioKillSwitch

def test_kill_switch_activation_and_recovery():
    ks = PortfolioKillSwitch()

    assert ks.is_halted is False
    assert ks.state == "NORMAL"

    # Activate
    st1 = ks.activate("Extreme market volatility circuit breaker")
    assert st1.is_active is True
    assert st1.state == "HALTED"

    # Recover
    st2 = ks.recover(authorized_by="Admin Risk Officer")
    assert st2.is_active is False
    assert st2.state == "NORMAL"
    assert len(st2.audit_events) == 2
