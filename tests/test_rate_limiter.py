import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.rate_limiter import tenant_rate_limiter

def test_tenant_rate_limiter():
    res = tenant_rate_limiter.check_rate_limit("ORG-101", 600)
    assert res["allowed"] is True
    assert res["remaining"] == 558
