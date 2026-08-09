import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.mlops.governance import ai_governance_audit

def test_ai_governance_audit():
    entry = ai_governance_audit.log_event("MOD-TEST-01", "TEST_ACTION", "Tester")
    assert entry["action"] == "TEST_ACTION"

    trail = ai_governance_audit.list_audit_trail()
    assert len(trail) >= 2
