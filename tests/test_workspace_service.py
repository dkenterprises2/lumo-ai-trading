import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.workspace_service import workspace_service

def test_workspace_service():
    ws_list = workspace_service.list_workspaces("org_acme")
    assert len(ws_list) >= 4
    new_ws = workspace_service.create_workspace("org_acme", "Alpha Lab")
    assert new_ws["workspace_id"] == "ws_alpha_lab"
