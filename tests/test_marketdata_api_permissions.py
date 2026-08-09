import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.rbac import rbac_manager

def test_marketdata_api_permissions():
    assert rbac_manager.check_permission("ANALYST", "marketdata:view") is True
    assert rbac_manager.check_permission("VIEWER", "marketdata:view") is True
