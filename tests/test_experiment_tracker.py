import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.experiments.experiment_tracker import experiment_tracker

def test_experiment_tracker():
    exps = experiment_tracker.list_experiments()
    assert len(exps) >= 1
    new_exp = experiment_tracker.create_experiment("Test Sweep")
    assert new_exp["name"] == "Test Sweep"
