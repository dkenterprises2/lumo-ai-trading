import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.exchange.binance_adapter import BinanceExchangeAdapter
from backend.exchange.bybit_adapter import BybitAdapter

def test_order_reconciliation():
    binance = BinanceExchangeAdapter(testnet=True)
    ord1 = binance.create_order("BTC/USDT", "BUY", 1000.0, client_order_id="RECON_101")
    reconciled = binance.reconcile_orders()
    assert len(reconciled) >= 1

    bybit = BybitAdapter(testnet=True)
    ord2 = bybit.create_order("ETH/USDT", "BUY", 500.0, client_order_id="RECON_102")
    bybit_reconciled = bybit.reconcile_orders()
    assert len(bybit_reconciled) >= 1
