import pytest
import time
from backend.telemetry.ws_metrics import WSMetricsManager
from backend.telemetry.heartbeat_manager import HeartbeatManager

def test_ws_metrics_client_registration():
    mgr = WSMetricsManager()
    assert mgr.connected_clients == 0
    mgr.register_client()
    assert mgr.connected_clients == 1
    mgr.register_client()
    assert mgr.connected_clients == 2
    mgr.unregister_client()
    assert mgr.connected_clients == 1

def test_ws_metrics_broadcast_and_uptime():
    mgr = WSMetricsManager()
    mgr.record_broadcast(10.0)
    metrics = mgr.get_metrics()
    assert metrics.total_messages_broadcast == 1
    assert metrics.stream_uptime_seconds >= 0.0

def test_ws_heartbeat_status():
    mgr = WSMetricsManager()
    mgr.record_heartbeat()
    metrics = mgr.get_metrics()
    assert metrics.heartbeat_ok is True
