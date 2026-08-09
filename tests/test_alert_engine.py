import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.observability.alerts import alert_engine

def test_alert_engine_trigger_and_list():
    alert = alert_engine.trigger_alert("CRITICAL", "Risk Engine", "Max drawdown breached")
    assert alert["severity"] == "CRITICAL"
    assert alert["status"] == "FIRING"

    active = alert_engine.get_active_alerts()
    assert len(active) >= 1
