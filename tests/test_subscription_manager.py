import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.subscription_manager import subscription_manager

def test_subscription_manager_plans_and_subscribe():
    plans = subscription_manager.list_plans()
    assert len(plans) == 3

    sub = subscription_manager.subscribe_org("ORG-101", "plan_enterprise")
    assert sub["status"] == "ACTIVE"
    assert sub["plan_id"] == "plan_enterprise"
