import pytest
from backend.portfolio_risk.kelly_sizing import KellySizingEngine

def test_fractional_kelly_caps():
    engine = KellySizingEngine()

    res = engine.compute_kelly_size(
        win_probability=0.60,
        win_loss_ratio=2.0,
        portfolio_equity=10000.0,
        kelly_fraction=0.25,
        max_cap_pct=10.0
    )

    # Raw Kelly = (2 * 0.6 - 0.4) / 2 = 0.4
    # Fractional (0.25x) = 0.10 (10%)
    assert res.raw_kelly == 0.4
    assert res.fractional_kelly == 0.10
    assert res.capped_allocation_usd == 1000.0
