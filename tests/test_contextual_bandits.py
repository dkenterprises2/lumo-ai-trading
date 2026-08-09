import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.alpha_factory.meta_learning.strategy_selector import strategy_selector

def test_contextual_regime_switch():
    sel = strategy_selector.select_strategies("LOW_VOLATILITY_BEAR")
    assert sel["regime"] == "LOW_VOLATILITY_BEAR"
