import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_network.oms.order_lifecycle import oms_engine

def test_oms_order_lifecycle():
    order = oms_engine.create_order("BTCUSDT", "BUY", 1.0, 64800.0)
    assert order["status"] == "CREATED"
    assert order["symbol"] == "BTCUSDT"
    cancelled = oms_engine.cancel_order(order["order_id"])
    assert cancelled["status"] == "CANCELLED"
