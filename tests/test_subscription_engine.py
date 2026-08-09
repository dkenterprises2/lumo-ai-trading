import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.subscription_engine import subscription_engine

def test_subscription_plan_change():
    res = subscription_engine.change_plan("org_test", "WHITE_LABEL")
    assert res["new_plan"] == "WHITE_LABEL"
    assert res["status"] == "ACTIVE"
