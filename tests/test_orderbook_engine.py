import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.marketdata.orderbook_engine import orderbook_engine

def test_orderbook_snapshot_and_update():
    book = orderbook_engine.get_orderbook("BTC/USDT", 5)
    assert len(book["bids"]) == 5
    assert len(book["asks"]) == 5
    assert book["sequence_id"] > 0

    upd = orderbook_engine.update_depth("BTC/USDT", [(64812.0, 1.0)], [(64813.0, 1.0)], 100051)
    assert upd is True
