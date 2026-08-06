import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution.advanced_orders import algo_execution_engine

def test_twap_iceberg_bracket_execution():
    twap_res = algo_execution_engine.execute_twap_order("BTC/USDT", "BUY", total_amount_usd=5000.0, slices_count=5)
    assert twap_res["order_type"] == "TWAP"
    assert len(twap_res["slices"]) == 5

    iceberg_res = algo_execution_engine.execute_iceberg_order("BTC/USDT", "BUY", total_amount_usd=10000.0, visible_clip_usd=2000.0)
    assert iceberg_res["order_type"] == "ICEBERG"
    assert iceberg_res["total_clips"] == 5

    bracket_res = algo_execution_engine.execute_bracket_order("BTC/USDT", "BUY", 1000.0, 65000.0, 63000.0, 68000.0)
    assert bracket_res["order_type"] == "BRACKET"
