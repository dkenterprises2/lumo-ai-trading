import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.multiasset.onchain_analytics import onchain_analytics

def test_onchain_analytics():
    data = onchain_analytics.get_analytics()
    assert "net_exchange_flow_24h_usd" in data
    assert "stablecoin_minted_24h_usd" in data
