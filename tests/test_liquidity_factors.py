import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.factors.factor_registry import factor_registry

def test_liquidity_factor():
    res = factor_registry.run_factor("amihud_illiquidity")
    assert res["status"] == "COMPLETED"
