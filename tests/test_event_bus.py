import sys
import os
import pytest
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.event_bus import event_bus, EventTypes

@pytest.mark.asyncio
async def test_event_bus_pub_sub():
    received_events = []

    async def on_market_tick(event):
        received_events.append(event)

    event_bus.subscribe(EventTypes.MARKET_TICK, on_market_tick)

    await event_bus.publish(EventTypes.MARKET_TICK, {"symbol": "BTC/USDT", "price": 65000.0})

    assert len(received_events) == 1
    assert received_events[0]["type"] == EventTypes.MARKET_TICK
    assert received_events[0]["data"]["price"] == 65000.0
