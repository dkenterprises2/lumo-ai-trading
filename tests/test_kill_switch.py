import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_agents.kill_switch import ai_kill_switch

def test_kill_switch_activation():
    assert ai_kill_switch.is_active() is False
    res = ai_kill_switch.activate()
    assert res["kill_switch_active"] is True
    assert ai_kill_switch.is_active() is True

    res2 = ai_kill_switch.deactivate()
    assert res2["kill_switch_active"] is False
    assert ai_kill_switch.is_active() is False
