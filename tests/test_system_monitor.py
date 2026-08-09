import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.admin.system_monitor import platform_system_monitor

def test_platform_system_monitor():
    health = platform_system_monitor.get_system_health()
    assert health["overall_health"] == "HEALTHY"
    assert health["database_status"] == "ONLINE"
    assert health["exchanges"]["binance"] == "CONNECTED"
