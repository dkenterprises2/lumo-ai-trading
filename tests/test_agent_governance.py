import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_agents.agent_governance import agent_governance

def test_agent_governance_approval():
    appr = agent_governance.approve_version("v3_model")
    assert appr["status"] == "APPROVED"
    rej = agent_governance.reject_version("v4_model")
    assert rej["status"] == "REJECTED"
