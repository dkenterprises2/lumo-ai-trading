import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_agents.ppo_agent import ppo_agent

def test_ppo_agent_epoch():
    ep = ppo_agent.train_epoch(10)
    assert ep["status"] == "COMPLETED"
    assert "actor_loss" in ep
