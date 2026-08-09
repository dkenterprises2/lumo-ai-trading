import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_agents.experience_replay import experience_replay

def test_experience_replay_buffer():
    experience_replay.add_experience({"obs": 1}, "BUY", 1.5, {"obs": 2}, False)
    assert experience_replay.size() >= 1
    batch = experience_replay.sample_batch(10)
    assert len(batch) >= 1
