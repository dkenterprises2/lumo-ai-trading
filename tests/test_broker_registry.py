import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_network.brokers.broker_registry import broker_registry

def test_broker_registry():
    brokers = broker_registry.list_brokers()
    assert len(brokers) >= 4
    conn = broker_registry.connect_broker("binance_main")
    assert conn["status"] == "CONNECTED"
