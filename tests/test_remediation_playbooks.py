import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_copilot.operations_ai.incident_detector import operations_ai

def test_remediation_trigger():
    res = operations_ai.remediate_incident("INC-P24-101")
    assert res["status"] == "REMEDIATION_TRIGGERED"
    assert "audit_ref" in res
