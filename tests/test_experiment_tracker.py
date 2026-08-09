import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.mlops.experiment_tracker import experiment_tracker

def test_experiment_tracker():
    exp = experiment_tracker.start_experiment("Test ML Experiment", "Description")
    assert exp["experiment_id"].startswith("EXP-")

    run = experiment_tracker.log_run(exp["experiment_id"], {"accuracy": 0.72}, {"lr": 0.01})
    assert run["run_id"].startswith("RUN-")
    assert run["metrics"]["accuracy"] == 0.72
