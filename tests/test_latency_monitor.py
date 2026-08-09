import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_algos.latency_monitor import latency_monitor

def test_latency_monitor():
    metrics = latency_monitor.get_latency_metrics()
    assert len(metrics) >= 3
    assert metrics[0]["venue"] == "Binance"
