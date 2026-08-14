import pytest
from backend.portfolio_risk.risk_budget import RiskBudgetTracker

def test_risk_budget_exhaustion():
    tracker = RiskBudgetTracker(default_daily_budget_pct=5.0)

    # $600 loss on $10,000 balance -> 6% loss >= 5% limit -> EXHAUSTED
    res = tracker.compute_budget(10000.0, daily_pnl_usd=-600.0)

    assert res.status == "EXHAUSTED"
    assert res.action == "BLOCK_NEW_TRADES"
    assert res.remaining_daily_pct == 0.0
