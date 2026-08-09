import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_copilot.orchestration.agent_registry import agentic_orchestrator

def test_agent_registry():
    agents = agentic_orchestrator.list_agents()
    assert len(agents) == 7
    assert "GovernanceAgent" in agents
