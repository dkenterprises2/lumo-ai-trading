import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_copilot.orchestration.agent_registry import agentic_orchestrator

def test_task_pipeline_order():
    wf = agentic_orchestrator.create_workflow("Task Order Test")
    assert wf["pipeline"][0] == "ResearchAgent"
    assert wf["pipeline"][-1] == "GovernanceAgent"
