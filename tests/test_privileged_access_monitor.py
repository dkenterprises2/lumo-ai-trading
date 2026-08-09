import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.compliance.privileged_access_monitor import privileged_access_monitor

def test_privileged_access_events():
    events = privileged_access_monitor.list_events("ORG-101")
    assert len(events) >= 1
    assert events[0]["actor"] == "admin@alphaquant.com"
