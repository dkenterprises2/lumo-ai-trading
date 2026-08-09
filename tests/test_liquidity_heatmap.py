import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.marketdata.liquidity_heatmap import liquidity_heatmap

def test_liquidity_heatmap():
    hm = liquidity_heatmap.get_heatmap("BTC/USDT")
    assert len(hm["heatmap_matrix"]) >= 2
    assert hm["heatmap_matrix"][0]["cluster_type"] == "SUPPORT"
