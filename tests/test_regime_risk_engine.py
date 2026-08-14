import pytest
from backend.portfolio_risk.regime_risk_engine import RegimeRiskEngine

def test_regime_risk_mapping():
    engine = RegimeRiskEngine(base_max_positions=10)

    # HIGH_VOLATILITY regime
    res_hv = engine.evaluate_regime_risk("HIGH_VOLATILITY")
    assert res_hv.position_size_multiplier == 0.50
    assert res_hv.max_concurrent_positions == 5

    # BULL regime
    res_bull = engine.evaluate_regime_risk("BULL")
    assert res_bull.position_size_multiplier == 1.0
    assert res_bull.max_concurrent_positions == 10
