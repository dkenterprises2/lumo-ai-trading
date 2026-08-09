import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.marketdata.microstructure_alpha import microstructure_alpha

def test_microstructure_alpha_signal():
    sig = microstructure_alpha.generate_signal("BTC/USDT")
    assert sig["signal"] == "SHORT_TERM_BULLISH"
    assert sig["confidence"] > 0.80
