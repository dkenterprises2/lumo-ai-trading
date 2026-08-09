import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_copilot.orchestration.agent_registry import agentic_orchestrator

def test_workflow_orchestration():
    wf = agentic_orchestrator.create_workflow("Test Workflow")
    assert wf["status"] == "ORCHESTRATED_AWAITING_GOVERNANCE_APPROVAL"
    assert len(wf["pipeline"]) == 4
