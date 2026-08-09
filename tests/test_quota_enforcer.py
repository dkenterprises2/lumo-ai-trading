import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.quota_enforcer import quota_enforcer

def test_quota_thresholds():
    q1 = quota_enforcer.check_quota("api_calls", 150000, 200000)
    assert q1["status"] == "OK"
    q2 = quota_enforcer.check_quota("api_calls", 200000, 200000)
    assert q2["status"] == "HARD_LIMIT_REACHED"
