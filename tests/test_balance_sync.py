import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.exchange.paper_adapter import PaperExchangeAdapter
from backend.exchange.bybit_adapter import BybitAdapter

def test_balance_synchronization():
    paper = PaperExchangeAdapter(initial_balance=15000.0)
    bal = paper.fetch_balance()
    assert bal["free_balance"] == 15000.0

    bybit = BybitAdapter(testnet=True)
    bybit_bal = bybit.fetch_balance()
    assert bybit_bal["total_wallet"] == 10000.0
