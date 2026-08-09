import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_network.sor.routing_optimizer import smart_order_router

def test_liquidity_aggregation():
    quote = smart_order_router.get_aggregated_quote("BTCUSDT")
    assert quote["best_bid"] > 0
    assert len(quote["venues"]) == 3
