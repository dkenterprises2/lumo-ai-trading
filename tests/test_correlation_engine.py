import pytest
from backend.portfolio_risk.correlation_engine import CorrelationEngine

def test_correlation_analysis_single_position():
    engine = CorrelationEngine()
    positions = {"BTC/USDT": {"notional_val_usd": 1000.0, "leverage": 1}}
    res = engine.analyze_positions_correlation(positions, 10000.0)

    assert "BTC/USDT" in res["symbol_risks"]
    assert res["correlation_risk_score"] == 0.0

def test_correlation_analysis_multiple_correlated_positions():
    engine = CorrelationEngine()
    positions = {
        "BTC/USDT": {"notional_val_usd": 2000.0, "leverage": 1},
        "ETH/USDT": {"notional_val_usd": 1500.0, "leverage": 1}
    }
    res = engine.analyze_positions_correlation(positions, 10000.0)

    assert res["average_correlation"] > 0.0
    assert "BTC/USDT" in res["symbol_risks"]
