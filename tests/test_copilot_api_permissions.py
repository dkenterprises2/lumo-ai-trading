import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.rbac import rbac_manager

def test_copilot_api_permissions():
    assert rbac_manager.check_permission("ADMIN", "copilot:manage") is True
    assert rbac_manager.check_permission("VIEWER", "copilot:manage") is False
    assert rbac_manager.check_permission("VIEWER", "copilot:view") is True
