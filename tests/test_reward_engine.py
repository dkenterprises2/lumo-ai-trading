import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_agents.reward_engine import reward_engine

def test_reward_shaping():
    rw = reward_engine.calculate_reward(10.0, 2.0, 1.0, 0.5, 0.2)
    assert rw > 0
