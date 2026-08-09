import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.multiasset.arbitrage_graph import arbitrage_graph

def test_arbitrage_graph_opportunities():
    opps = arbitrage_graph.find_opportunities()
    assert len(opps) >= 1
    assert opps[0]["net_spread_bps"] > 0
