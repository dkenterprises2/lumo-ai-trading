import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.platform.metrics_collector import metrics_collector

def test_metrics_summary():
    m = metrics_collector.get_metrics_summary()
    assert m["http_requests_total"] > 0
    assert m["http_latency_p99_ms"] < 100
