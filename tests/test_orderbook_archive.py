import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.marketdata.orderbook_archive import orderbook_archive

def test_orderbook_archive():
    res = orderbook_archive.archive_orderbook("BTC/USDT")
    assert res["status"] == "SUCCESS"
    assert res["archived_snapshots"] > 0
