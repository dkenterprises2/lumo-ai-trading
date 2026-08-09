import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_agents.portfolio_rl_agent import portfolio_rl_agent

def test_portfolio_allocation():
    w = portfolio_rl_agent.allocate_weights()
    assert sum(w.values()) == 1.0
    assert w["BTC"] == 0.50
