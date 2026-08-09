import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.pairs_trading import pairs_trading_manager

def test_pairs_trading_evaluation():
    eval_res = pairs_trading_manager.evaluate_pair("BTC/USDT", "ETH/USDT")
    assert eval_res["status"] == "ACTIVE_MONITORING"
