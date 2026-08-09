import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_network.fix.fix_gateway import fix_gateway

def test_fix_message_parser():
    res = fix_gateway.parse_message("8=FIX.4.4|35=D|55=BTCUSDT|38=100|")
    assert res["parsed"] is True
    assert res["symbol"] == "BTCUSDT"
