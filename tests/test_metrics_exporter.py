import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.observability.metrics import metrics_exporter

def test_prometheus_metrics_exporter():
    metrics = metrics_exporter.generate_prometheus_metrics()
    assert "lumo_http_requests_total" in metrics
    assert "lumo_active_websocket_connections" in metrics
    assert "lumo_trades_executed_total" in metrics
