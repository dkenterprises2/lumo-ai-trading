import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.alpha_factory.marketplace.strategy_catalog import strategy_catalog

def test_strategy_catalog():
    strats = strategy_catalog.list_strategies()
    assert len(strats) >= 1
    pub = strategy_catalog.publish_strategy("alpha_momentum_v12")
    assert pub["status"] == "PUBLISHED_SIMULATED"
