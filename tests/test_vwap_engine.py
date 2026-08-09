import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_algos.vwap_engine import vwap_engine

def test_vwap_schedule():
    res = vwap_engine.calculate_vwap_schedule(50.0)
    assert res["algo"] == "VWAP"
    sum_qty = sum(s["quantity"] for s in res["slices"])
    assert abs(sum_qty - 50.0) < 1e-4
