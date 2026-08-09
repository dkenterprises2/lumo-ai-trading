import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.usage_metering import usage_metering_engine

def test_usage_metering_summary():
    summary = usage_metering_engine.get_usage_summary("ORG-101")
    assert summary["api_calls_used"] < summary["api_calls_quota"]
    assert summary["active_trading_bots"] <= summary["bots_quota"]
