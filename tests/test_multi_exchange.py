import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.exchange.multi_exchange import multi_exchange_manager, UnifiedExchangeAdapter

def test_multi_exchange_health_and_ordering():
    health = multi_exchange_manager.get_all_exchange_health()
    assert "BINANCE_SPOT" in health
    assert "BYBIT" in health
    assert "OKX" in health

    bybit = multi_exchange_manager.get_adapter("BYBIT")
    ord_res = bybit.create_order("BTC/USDT", "BUY", 1000.0, client_order_id="BYBIT_ORD_101")
    assert ord_res["status"] == "success"
    assert ord_res["client_order_id"] == "BYBIT_ORD_101"
