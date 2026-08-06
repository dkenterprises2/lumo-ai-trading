import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.alerting import alert_manager

def test_alert_manager_configuration_and_dispatch():
    alert_manager.configure(generic_webhook="https://example.com/webhook")
    res = alert_manager.send_alert("ORDER_OPENED", "New Position", "BUY BTC/USDT at $65000.00")

    assert res["status"] == "success"
    assert res["alert_type"] == "ORDER_OPENED"
    assert "payload" in res
