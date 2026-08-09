import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.factors.factor_registry import factor_registry

def test_factor_registry():
    factors = factor_registry.list_factors()
    assert len(factors) >= 4
    run = factor_registry.run_factor("momentum_20d")
    assert run["status"] == "COMPLETED"
