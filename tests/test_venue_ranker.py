import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_network.sor.routing_optimizer import smart_order_router

def test_venue_ranking():
    route = smart_order_router.route_order("BTCUSDT", 10.0, "BUY")
    assert "BINANCE" in route["routed_venues"]
