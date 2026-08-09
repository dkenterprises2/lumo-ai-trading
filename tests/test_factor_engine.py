import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.factor_engine import factor_engine

def test_factor_engine_calculations():
    res = factor_engine.calculate_factors([100.0, 102.0, 104.0, 103.0, 105.0])
    assert "momentum_1d" in res
    assert "value_zscore" in res
    assert "realized_volatility" in res
