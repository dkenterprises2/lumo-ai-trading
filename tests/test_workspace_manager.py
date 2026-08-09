import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.notebooks.workspace_manager import workspace_manager

def test_workspace_manager():
    wss = workspace_manager.list_workspaces()
    assert len(wss) >= 1
    assert "collaborators" in wss[0]
