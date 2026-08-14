import pytest
from backend.portfolio_risk.leverage_engine import LeverageEngine

def test_leverage_reduction():
    engine = LeverageEngine()

    # High volatility & drawdown -> cap leverage
    res = engine.evaluate_leverage(
        requested_leverage=10,
        user_max_leverage=10,
        volatility_multiplier=0.6,
        drawdown_pct=6.0,
        portfolio_heat_status="HIGH"
    )

    # Must be reduced significantly below requested 10x
    assert res.recommended < 10.0
    assert res.recommended <= res.maximum_allowed
