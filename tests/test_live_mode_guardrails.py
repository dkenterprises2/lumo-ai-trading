import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_network.environment.environment_manager import environment_manager

def test_live_mode_guardrails():
    sw = environment_manager.request_switch("LIVE")
    assert sw["switched"] is False
    assert sw["status"] == "GOVERNANCE_APPROVAL_REQUIRED"
