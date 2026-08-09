import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_algos.pov_engine import pov_engine

def test_pov_slice_cap():
    res = pov_engine.calculate_pov_slice(100.0, target_participation_pct=25.0, max_participation_cap=20.0)
    assert res["effective_participation_pct"] == 20.0
    assert res["slice_quantity"] == 20.0
