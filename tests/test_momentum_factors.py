import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.factors.factor_registry import factor_registry

def test_momentum_factor():
    res = factor_registry.run_factor("momentum_20d")
    assert res["ic_mean"] > 0
