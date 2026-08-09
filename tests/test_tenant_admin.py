import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.admin.tenant_admin import tenant_admin_console

def test_tenant_admin_suspend_and_activate():
    susp = tenant_admin_console.suspend_tenant("ORG-101")
    assert susp["status"] == "SUSPENDED"

    act = tenant_admin_console.activate_tenant("ORG-101")
    assert act["status"] == "ACTIVE"

    users = tenant_admin_console.list_users()
    assert len(users) >= 2
