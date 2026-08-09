import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_agents.agent_orchestrator import agent_orchestrator

def test_agent_orchestrator():
    st = agent_orchestrator.get_status()
    assert st["status"] == "OPERATIONAL"
    assert st["active_agents"] == 4
