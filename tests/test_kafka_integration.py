import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.eventbus.kafka_bus import kafka_bus
from backend.eventbus.contracts import RiskAlertEvent

def test_kafka_integration_fallback():
    evt = RiskAlertEvent(event_id="ALERT-1", alert_level="WARNING", message="Daily loss limit near threshold")
    pub = kafka_bus.publish("risk.alerts", evt)
    assert pub is True
