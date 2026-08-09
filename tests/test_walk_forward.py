import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.walk_forward import walk_forward_optimizer

def test_walk_forward_optimization():
    wfo = walk_forward_optimizer.run_walk_forward()
    assert wfo["status"] == "COMPLETED"
    assert wfo["out_of_sample_sharpe"] > 0
