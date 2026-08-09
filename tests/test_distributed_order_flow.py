import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.eventbus.contracts import OrderCreatedEvent, OrderFilledEvent
from backend.eventbus.redis_streams_bus import redis_streams_bus

def test_distributed_order_flow():
    received = []
    redis_streams_bus.subscribe("orders.filled", lambda p: received.append(p))

    evt = OrderFilledEvent(
        event_id="EVT-202",
        order_id="ORD-202",
        fill_price=64800.0,
        filled_quantity=0.1,
        fee=0.32
    )
    redis_streams_bus.publish("orders.filled", evt)
    assert len(received) == 1
    assert received[0]["fill_price"] == 64800.0
