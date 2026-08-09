import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.tenant_context import current_tenant_context

def test_tenant_context_resolution():
    d = current_tenant_context.to_dict()
    assert "tenant_id" in d
    assert d["plan"] == "ENTERPRISE"
