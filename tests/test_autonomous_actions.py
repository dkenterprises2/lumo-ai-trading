import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_copilot.operations_ai.incident_detector import operations_ai

def test_autonomous_actions_policy():
    incidents = operations_ai.get_incidents()
    assert incidents[0]["requires_approval"] is True
