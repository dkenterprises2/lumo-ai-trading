import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.notebooks.workspace_manager import workspace_manager

def test_collaboration_workspaces():
    wss = workspace_manager.list_workspaces()
    assert wss[0]["workspace_id"] == "ws_quant_alpha"
