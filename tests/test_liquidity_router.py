import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_algos.liquidity_router import liquidity_router

def test_liquidity_router_scoring():
    venues = liquidity_router.score_venues()
    assert len(venues) >= 3
    assert venues[0]["venue"] == "Binance"
