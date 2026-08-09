import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_agents.shadow_learning_agent import shadow_learning_agent

def test_shadow_learning_no_live_orders():
    tr = shadow_learning_agent.record_shadow_decision("ETH/USDT", "BUY_SMALL", 3450.0)
    assert tr["trade_id"].startswith("SHADOW-")
    assert tr["status"] == "RECORDED"
