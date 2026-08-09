import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution.smart_router import smart_order_router

def test_smart_order_router():
    routed = smart_order_router.route_order("BTC/USDT", "BUY", 0.05, routing_policy="BEST_PRICE")
    assert routed["routed_exchange"] in smart_order_router.SUPPORTED_EXCHANGES
    assert routed["estimated_price"] > 0
    assert routed["estimated_fee_bps"] > 0
