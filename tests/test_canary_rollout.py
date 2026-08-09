import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.mlops.canary_rollout import canary_rollout_engine

def test_canary_rollout_engine():
    res = canary_rollout_engine.start_canary("MOD-CANDIDATE-01", 15.0)
    assert res["status"] == "CANARY_ACTIVE"
    assert res["traffic_allocation_pct"] == 15.0
