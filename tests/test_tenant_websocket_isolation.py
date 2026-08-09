import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.tenant_middleware import tenant_middleware

def test_tenant_websocket_channel_isolation():
    ctx1 = tenant_middleware.get_tenant_context("ORG-101")
    ctx2 = tenant_middleware.get_tenant_context("ORG-102")
    assert ctx1["websocket_channel"] != ctx2["websocket_channel"]
