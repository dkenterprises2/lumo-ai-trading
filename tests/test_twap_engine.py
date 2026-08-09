import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_algos.twap_engine import twap_engine

def test_twap_slicing_conservation():
    res = twap_engine.slice_twap_order(10.0, duration_minutes=60, interval_seconds=300, randomize_slices=True)
    assert res["num_slices"] == 12
    sum_qty = sum(s["quantity"] for s in res["slices"])
    assert abs(sum_qty - 10.0) < 1e-5
