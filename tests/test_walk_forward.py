import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.alpha_factory.validation.walk_forward import walk_forward_engine

def test_walk_forward_validation():
    res = walk_forward_engine.run_walk_forward("alpha_momentum_v12")
    assert res["status"] == "VALIDATED"
    assert res["out_of_sample_sharpe"] > 1.5
