import pytest
from backend.portfolio_risk.position_sizing import PositionSizingEngine

def test_position_sizing_combines_multipliers():
    engine = PositionSizingEngine()
    res = engine.compute_size(
        base_allocation_usd=1000.0,
        portfolio_equity=10000.0,
        max_capital_per_trade_pct=10.0,
        volatility_mult=0.6,
        drawdown_mult=0.8,
        streak_mult=1.0,
        regime_mult=1.0
    )

    # 1000 * 0.6 * 0.8 = 480
    assert res.recommended_allocation_usd == 480.0
    assert res.scaling_factors["combined"] == 0.48
