import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai.research_workspace import research_workspace_manager

def test_research_workspace_projects():
    user_id = 991
    proj = research_workspace_manager.create_project(user_id, "Volatility Spread Alpha", "Test spread mean-reversion", "FUTURES")
    assert proj["title"] == "Volatility Spread Alpha"
    assert proj["status"] == "ACTIVE"

    projects = research_workspace_manager.list_projects(user_id)
    assert len(projects) >= 1
