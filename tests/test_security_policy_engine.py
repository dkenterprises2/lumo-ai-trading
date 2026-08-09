import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.security.security_policy_engine import security_policy_engine

def test_security_policy_engine():
    policies = security_policy_engine.list_policies()
    assert len(policies) == 3
    assert policies[0]["enforced"] is True
