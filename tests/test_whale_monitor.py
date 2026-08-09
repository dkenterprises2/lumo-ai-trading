import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.multiasset.whale_monitor import whale_monitor

def test_whale_alerts():
    alerts = whale_monitor.list_alerts()
    assert len(alerts) >= 1
    assert alerts[0]["symbol"] == "BTC"
