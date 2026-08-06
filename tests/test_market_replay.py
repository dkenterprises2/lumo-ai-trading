import sys
import os
import pytest
import asyncio
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from market_replay import MarketReplayEngine

@pytest.mark.asyncio
async def test_market_replay_engine():
    replay_engine = MarketReplayEngine()

    ticks = [
        {"price": 60000.0, "timestamp": time.time() - 200, "rsi": 25.0},
        {"price": 61000.0, "timestamp": time.time() - 100, "rsi": 30.0},
        {"price": 62000.0, "timestamp": time.time(), "rsi": 40.0}
    ]

    res = await replay_engine.replay_ticks("BTC/USDT", ticks)

    assert res["status"] == "success"
    assert res["replayed_ticks_count"] == 3
    assert res["generated_signals_count"] == 3
