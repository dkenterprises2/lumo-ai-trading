import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.marketdata.orderbook_imbalance import orderbook_imbalance

def test_orderbook_imbalance():
    imb = orderbook_imbalance.get_imbalance("BTC/USDT")
    assert "imbalance_ratio" in imb
    assert "pressure_signal" in imb
