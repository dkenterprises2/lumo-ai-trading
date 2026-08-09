import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.mlops.inference_monitor import inference_performance_monitor

def test_inference_performance_monitor():
    perf = inference_performance_monitor.get_performance_metrics()
    assert perf["avg_inference_latency_ms"] > 0
    assert perf["throughput_qps"] > 0
