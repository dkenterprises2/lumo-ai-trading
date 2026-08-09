import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.tenant_middleware import tenant_middleware

def test_tenant_context_isolation():
    ctx = tenant_middleware.get_tenant_context("ORG-999")
    assert ctx["tenant_id"] == "ORG-999"
    assert ctx["is_isolated"] is True
    assert ctx["websocket_channel"] == "tenant:ORG-999"
