import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.marketdata.marketdata_orchestrator import marketdata_orchestrator

def test_marketdata_orchestrator():
    st = marketdata_orchestrator.get_status()
    assert st["status"] == "OPERATIONAL"
    assert len(st["active_feeds"]) >= 3
