import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.marketdata.feed_normalizer import feed_normalizer

def test_feed_normalizer():
    norm = feed_normalizer.normalize_tick("Binance", {"s": "BTC/USDT", "p": "64810.5", "q": "0.2"})
    assert norm["exchange"] == "Binance"
    assert norm["price"] == 64810.5
    assert norm["normalized"] is True
