import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.monitoring import metrics_collector

def test_metrics_collector():
    metrics_collector.record_ai_latency(0.04)
    metrics_collector.record_risk_latency(0.01)
    metrics_collector.increment_orders()
    metrics_collector.increment_trades()

    metrics = metrics_collector.get_system_metrics()

    assert metrics["status"] == "HEALTHY"
    assert "latencies_ms" in metrics
    assert metrics["latencies_ms"]["ai_engine"] >= 0.0
    assert metrics["counters"]["total_orders"] >= 1
    assert metrics["counters"]["total_trades"] >= 1
