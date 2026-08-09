import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_copilot.operations_ai.incident_detector import operations_ai

def test_incident_detection():
    incidents = operations_ai.get_incidents()
    assert len(incidents) >= 1
    assert incidents[0]["severity"] == "HIGH"
