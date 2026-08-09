import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.rbac import rbac_manager

def test_rbac_permissions():
    assert rbac_manager.check_permission("OWNER", "any:perm") is True
    assert rbac_manager.check_permission("TRADER", "trading:execute") is True
    assert rbac_manager.check_permission("VIEWER", "trading:execute") is False
