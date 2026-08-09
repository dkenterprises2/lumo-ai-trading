import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.compliance.api_audit_logger import api_access_audit_logger

def test_api_access_audit_logs():
    logs = api_access_audit_logger.list_logs("ORG-101")
    assert len(logs) >= 1
    assert logs[0]["endpoint"] == "/api/v1/orders"
