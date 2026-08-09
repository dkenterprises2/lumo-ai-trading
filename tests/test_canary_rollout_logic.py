import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.platform.canary_controller import canary_controller

def test_canary_rollout():
    c = canary_controller.start_canary("lumo-api", 10)
    assert c["current_split_pct"] == 10
    assert c["status"] == "CANARY_IN_PROGRESS"
