import pytest
from backend.portfolio_risk.volatility_engine import VolatilityEngine

def test_volatility_scaling():
    engine = VolatilityEngine()

    # Extreme volatility
    res_ext = engine.analyze_volatility(atr_pct=7.0, realized_vol_pct=65.0)
    assert res_ext.volatility_regime == "EXTREME"
    assert res_ext.position_size_multiplier == 0.30

    # Normal volatility
    res_norm = engine.analyze_volatility(atr_pct=2.0, realized_vol_pct=20.0)
    assert res_norm.volatility_regime == "NORMAL"
    assert res_norm.position_size_multiplier == 1.0
