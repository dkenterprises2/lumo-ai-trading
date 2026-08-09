import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.marketdata.dom_processor import dom_processor

def test_dom_processor_metrics():
    dom = dom_processor.process_dom("BTC/USDT")
    assert "spread" in dom
    assert "depth_imbalance" in dom
    assert dom["spread"] >= 0
