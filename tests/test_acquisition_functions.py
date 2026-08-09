import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.alpha_factory.optimization.bayesian_optimizer import bayesian_optimizer

def test_trials_count():
    res = bayesian_optimizer.run_optimization("alpha_test")
    assert res["trials_completed"] == 100
