import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.mlops.shadow_deployment import shadow_deployment_framework

def test_shadow_deployment_framework():
    res = shadow_deployment_framework.deploy_shadow_model("MOD-CANDIDATE-01")
    assert res["status"] == "DEPLOYED"
    assert res["traffic_split_pct"] == 100.0
