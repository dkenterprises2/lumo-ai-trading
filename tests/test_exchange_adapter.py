import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from trader import PaperTrader
from backend.exchange.paper_adapter import PaperExchangeAdapter
from backend.exchange.binance_adapter import BinanceExchangeAdapter

def test_paper_exchange_adapter():
    trader = PaperTrader(initial_balance=10000.0)
    adapter = PaperExchangeAdapter(trader)

    assert adapter.get_exchange_name() == "PAPER_EXCHANGE"

    bal = adapter.fetch_balance()
    assert bal["total_equity"] == 10000.0

    order_res = adapter.create_order("BTC/USDT", "BUY", 1000.0, leverage=1)
    assert order_res["status"] == "success"

def test_binance_exchange_adapter():
    adapter = BinanceExchangeAdapter(testnet=True)

    assert adapter.get_exchange_name() == "BINANCE_TESTNET"

    ticker = adapter.fetch_ticker("BTC/USDT")
    assert ticker["symbol"] == "BTC/USDT"

    ord_res = adapter.create_order("BTC/USDT", "BUY", 1000.0)
    assert ord_res["status"] == "success"
