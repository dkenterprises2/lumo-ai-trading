import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_agents.trend_following_agent import trend_following_agent

def test_trading_env_observation():
    obs = {"ohlcv": [64800, 64810], "regime": "BULL"}
    act = trend_following_agent.predict(obs)
    assert act == "BUY_SMALL"
