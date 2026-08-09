import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.compliance.trade_surveillance import trade_surveillance_engine

def test_trade_surveillance_alerts():
    alerts = trade_surveillance_engine.list_alerts("ORG-101")
    assert len(alerts) >= 1
    assert alerts[0]["pattern"] == "WASH_TRADING_PATTERN"

    res = trade_surveillance_engine.resolve_alert(alerts[0]["alert_id"])
    assert res["status"] == "RESOLVED"
