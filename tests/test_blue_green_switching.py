import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.platform.deployment_service import deployment_service

def test_deployment_rollback():
    res = deployment_service.rollback("dep-101")
    assert res["status"] == "ROLLED_BACK"
    assert res["traffic_split_pct"] == 0
