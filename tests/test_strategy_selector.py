import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.alpha_factory.meta_learning.strategy_selector import strategy_selector

def test_meta_strategy_selector():
    sel = strategy_selector.select_strategies("HIGH_VOLATILITY_BULL")
    assert len(sel["selected_strategies"]) == 2
    assert sel["confidence"] > 0.8
