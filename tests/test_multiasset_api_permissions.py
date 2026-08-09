import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.rbac import rbac_manager

def test_multiasset_api_permissions():
    assert rbac_manager.check_permission("TRADER", "multiasset:trade") is True
    assert rbac_manager.check_permission("VIEWER", "multiasset:trade") is False
    assert rbac_manager.check_permission("VIEWER", "multiasset:view") is True
