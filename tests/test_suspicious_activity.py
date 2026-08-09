import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.compliance.suspicious_activity import suspicious_activity_framework

def test_suspicious_activity_escalation():
    reports = suspicious_activity_framework.list_reports()
    assert len(reports) >= 1

    esc = suspicious_activity_framework.escalate_report(reports[0]["report_id"])
    assert esc["status"] == "ESCALATED_TO_FIU"
