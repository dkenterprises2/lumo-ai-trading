import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.marketdata.tick_ingestion import tick_ingestion_engine

def test_tick_ingestion():
    t = tick_ingestion_engine.ingest_tick("BTC/USDT", 64812.0, 0.5, "BUY")
    assert t["tick_id"].startswith("TICK-")
    ticks = tick_ingestion_engine.get_recent_ticks("BTC/USDT")
    assert len(ticks) >= 2
