import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_algos.replay_engine import replay_engine

def test_replay_engine():
    rep = replay_engine.replay_scenario("ORD-101")
    assert rep["status"] == "COMPLETED"
    assert rep["replay_id"].startswith("REPLAY-")
