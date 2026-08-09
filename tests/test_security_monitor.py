import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.admin.security_monitor import security_monitor_console

def test_security_monitor_events():
    events = security_monitor_console.list_security_events()
    assert len(events) >= 1
    assert events[0]["action"] == "SUPER_ADMIN_LOGIN"
