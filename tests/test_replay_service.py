import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.marketdata.replay_service import replay_service

def test_replay_service_controls():
    sess = replay_service.start_replay("BTC/USDT", 2.0)
    sid = sess["session_id"]
    assert sess["status"] == "RUNNING"

    paused = replay_service.pause_session(sid)
    assert paused["status"] == "PAUSED"

    resumed = replay_service.resume_session(sid)
    assert resumed["status"] == "RUNNING"
