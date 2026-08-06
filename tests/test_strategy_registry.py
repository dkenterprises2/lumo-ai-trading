import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.plugins.strategy_registry import strategy_registry

def test_strategy_registry_builtins():
    strats = strategy_registry.list_strategies()
    assert len(strats) == 8

    ids = [s["id"] for s in strats]
    assert "ai_hybrid" in ids
    assert "trend_following" in ids
    assert "mean_reversion" in ids
    assert "breakout" in ids
    assert "momentum" in ids
    assert "scalping" in ids
    assert "grid_trading" in ids
    assert "swing_trading" in ids

    ai_strat = strategy_registry.get_strategy("ai_hybrid")
    assert ai_strat is not None
    sig = ai_strat.generate_signal("BTC/USDT", {})
    assert sig["action"] == "BUY"
