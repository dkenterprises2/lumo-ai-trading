import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_network.replay.execution_replayer import execution_replayer

def test_execution_replay():
    rep = execution_replayer.replay_order("ord_p23_101")
    assert rep["status"] == "REPLAYED"
    assert rep["deterministic_match"] is True
    tl = execution_replayer.get_timeline("ord_p23_101")
    assert len(tl) == 5
