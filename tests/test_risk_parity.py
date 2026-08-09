import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.portfolio.risk_parity import risk_parity_allocator

def test_risk_parity_allocator():
    strategies = [
        {"id": "strat_high_vol", "volatility": 0.30},
        {"id": "strat_low_vol", "volatility": 0.10}
    ]
    res = risk_parity_allocator.calculate_risk_parity_weights(strategies)
    weights = res["weights"]
    assert weights["strat_low_vol"] > weights["strat_high_vol"]
    assert sum(weights.values()) == pytest.approx(1.0, abs=1e-3)
