import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.permission_registry import permission_registry

def test_permission_catalog():
    perms = permission_registry.list_permissions()
    assert len(perms) >= 5
    assert perms[0]["resource"] == "execution.orders"
