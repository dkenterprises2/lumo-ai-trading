import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai.research_agents import StrategyGeneratorAgent

def test_strategy_generator_agent():
    agent = StrategyGeneratorAgent()
    res = agent.run("Dual EMA Crossover with RSI confirmation")
    assert res["agent"] == "StrategyGeneratorAgent"
    assert "proposed_rules" in res
    assert res["proposed_rules"]["stop_loss_pct"] > 0
