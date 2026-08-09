import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_agents.safety_guardrails import safety_guardrails

def test_safety_guardrails():
    events = safety_guardrails.list_safety_events()
    assert len(events) >= 1
    assert events[0]["rule"] == "MAX_DAILY_LOSS_EXCEEDED"
