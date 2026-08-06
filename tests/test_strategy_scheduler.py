import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.plugins.strategy_manager import strategy_orchestrator

def test_strategy_orchestrator_execution_and_toggle():
    user_id = 901
    strats = strategy_orchestrator.get_user_strategies(user_id)
    assert len(strats) == 8

    # Test disable / pause
    dis_res = strategy_orchestrator.disable_strategy(user_id, "trend_following")
    assert dis_res["state"] == "PAUSED"

    # Test enable
    en_res = strategy_orchestrator.enable_strategy(user_id, "trend_following")
    assert en_res["state"] == "RUNNING"

    # Execute all active strategies
    signals = strategy_orchestrator.execute_all_strategies(user_id, "BTC/USDT", {})
    assert len(signals) >= 1
