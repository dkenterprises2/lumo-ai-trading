import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.alpha_factory.validation.walk_forward import walk_forward_engine

def test_overfitting_probability():
    res = walk_forward_engine.run_walk_forward("alpha_test")
    assert res["overfitting_prob_pct"] < 30.0
