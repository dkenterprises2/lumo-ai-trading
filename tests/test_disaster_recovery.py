import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.disaster_recovery import disaster_recovery

def test_disaster_recovery_drill():
    st = disaster_recovery.get_dr_status()
    assert st["rpo_seconds"] == 15
    assert st["last_drill_status"] == "PASSED_SIMULATED"
