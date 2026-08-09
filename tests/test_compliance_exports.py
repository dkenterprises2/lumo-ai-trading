import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.compliance.export_engine import compliance_export_engine

def test_compliance_export_engine():
    exp = compliance_export_engine.export_audit_trail("ORG-101", "CSV")
    assert exp["status"] == "COMPLETED"
    assert exp["format"] == "CSV"
