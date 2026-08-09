import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.mlops.reinforcement_lab import reinforcement_lab

def test_reinforcement_lab_experiment():
    res = reinforcement_lab.run_rl_experiment(episodes=50)
    assert res["episodes_completed"] == 50
    assert res["status"] == "EXPERIMENT_COMPLETED"
