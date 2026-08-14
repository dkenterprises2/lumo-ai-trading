import pytest
from backend.portfolio_risk.concentration_engine import ConcentrationEngine

def test_concentration_thresholds():
    engine = ConcentrationEngine()

    # 45% concentration -> HIGH
    positions = {"BTC/USDT": {"notional_val_usd": 4500.0, "leverage": 1}}
    res = engine.evaluate_concentration(positions, 10000.0)

    assert res.single_symbol_max_pct == 45.0
    assert res.status == "HIGH"
    assert len(res.warning_messages) > 0
