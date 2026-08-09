import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution.kill_switch import emergency_kill_switch

def test_emergency_kill_switch():
    act_res = emergency_kill_switch.activate("TEST_TRIGGER")
    assert emergency_kill_switch.is_active is True
    assert act_res["status"] == "KILL_SWITCH_ACTIVATED"

    deact_res = emergency_kill_switch.deactivate()
    assert emergency_kill_switch.is_active is False
    assert deact_res["status"] == "KILL_SWITCH_DEACTIVATED"
