import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.marketdata.websocket_fanout import websocket_fanout

def test_websocket_fanout():
    res = websocket_fanout.fanout_channel("marketdata:dom:BTCUSDT", {"mid_price": 64810.0})
    assert res is True
