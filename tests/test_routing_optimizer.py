import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_network.sor.routing_optimizer import smart_order_router

def test_routing_optimization():
    route = smart_order_router.route_order("BTCUSDT", 10.0, "BUY")
    assert route["status"] == "OPTIMALLY_ROUTED"
    assert route["estimated_slippage_bps"] == 1.2
