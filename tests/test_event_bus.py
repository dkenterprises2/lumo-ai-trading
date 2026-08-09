import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.eventbus.contracts import OrderCreatedEvent
from backend.eventbus.event_router import event_router

def test_event_bus_dispatch():
    evt = OrderCreatedEvent(
        event_id="EVT-101",
        order_id="ORD-101",
        symbol="BTC/USDT",
        side="BUY",
        quantity=0.1,
        order_type="LIMIT"
    )
    res = event_router.dispatch_event("orders.created", evt)
    assert res is True
