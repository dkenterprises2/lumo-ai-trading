import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.exchange.binance_adapter import BinanceExchangeAdapter

def test_binance_adapter_ticker_balance_order():
    adapter = BinanceExchangeAdapter(testnet=True)
    assert adapter.get_exchange_name() == "BINANCE_TESTNET"

    ticker = adapter.fetch_ticker("BTC/USDT")
    assert ticker["symbol"] == "BTC/USDT"
    assert ticker["last"] > 0

    bal = adapter.fetch_balance()
    assert bal["free_balance"] == 10000.0

    ord_res = adapter.create_order("BTC/USDT", "BUY", 1000.0, client_order_id="BINANCE_CLIENT_101")
    assert ord_res["status"] == "success" or ord_res["status"] == "FILLED"
