import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.admin.platform_admin import platform_admin_console

def test_platform_admin_metrics():
    metrics = platform_admin_console.get_platform_metrics()
    assert metrics["total_tenants"] == 48
    assert metrics["platform_uptime_pct"] > 99.0
