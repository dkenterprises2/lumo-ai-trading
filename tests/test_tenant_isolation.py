import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.tenant_router import tenant_router_service

def test_tenant_isolation():
    t1 = tenant_router_service.resolve_tenant("acme.lumo.trade")
    t2 = tenant_router_service.resolve_tenant("alpha.lumo.trade")
    assert t1.tenant_id != t2.tenant_id
    assert t1.organization_slug == "acme"
    assert t2.organization_slug == "alpha"
