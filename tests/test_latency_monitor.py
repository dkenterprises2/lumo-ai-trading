import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution.latency_monitor import latency_monitor

def test_latency_monitor():
    latency_monitor.record_latency("binance_spot", "ORDER_SUBMIT", 15.4)
    latency_monitor.record_latency("binance_spot", "ORDER_SUBMIT", 20.6)

    summary = latency_monitor.get_latency_summary()
    assert summary["overall_avg_ms"] == 18.0
