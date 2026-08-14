import pytest
from backend.portfolio_risk.drawdown_engine import DrawdownEngine

def test_drawdown_tiers():
    engine = DrawdownEngine()

    # 3% drawdown -> 80% multiplier
    res1 = engine.compute_drawdown_adjustment(3.0)
    assert res1.risk_multiplier == 0.80

    # 6% drawdown -> 50% multiplier
    res2 = engine.compute_drawdown_adjustment(6.0)
    assert res2.risk_multiplier == 0.50

    # 11% drawdown -> HALTED
    res3 = engine.compute_drawdown_adjustment(11.0)
    assert res3.risk_multiplier == 0.0
    assert res3.trading_status == "HALTED"
