import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.bayesian_optimizer import bayesian_optimizer

def test_bayesian_optimization():
    res = bayesian_optimizer.optimize(10)
    assert res["convergence_reached"] is True
    assert "best_params" in res
