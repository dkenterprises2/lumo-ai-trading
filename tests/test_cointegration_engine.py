import sys
import os
import pytest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.cointegration_engine import cointegration_engine

def test_cointegration_engine():
    a = np.array([10, 12, 14, 16, 18, 20])
    b = np.array([20, 24, 28, 32, 36, 40])
    res = cointegration_engine.test_cointegration(a, b)
    assert res["cointegrated"] is True
    assert "hedge_ratio" in res
