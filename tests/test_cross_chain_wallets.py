import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.multiasset.cross_chain_wallets import cross_chain_wallets

def test_cross_chain_wallets():
    wallets = cross_chain_wallets.list_wallets()
    assert len(wallets) >= 2
    assert wallets[0]["chain"] == "ETHEREUM"
