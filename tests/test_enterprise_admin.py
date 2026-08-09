import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.enterprise_admin import enterprise_admin

def test_enterprise_admin():
    health = enterprise_admin.get_system_health()
    assert health["total_tenants"] >= 12
    assert health["system_health"] == "HEALTHY"
