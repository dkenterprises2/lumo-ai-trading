import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_agents.policy_gradient import policy_gradient_agent

def test_policy_gradient_training():
    res = policy_gradient_agent.train_step([])
    assert "policy_loss" in res
    assert res["policy_loss"] > 0
