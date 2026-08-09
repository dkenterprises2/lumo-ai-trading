import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.observability.health import health_aggregator

def test_health_check_probes():
    live = health_aggregator.get_liveness_status()
    assert live["status"] == "UP"

    ready = health_aggregator.get_readiness_status()
    assert ready["status"] == "UP"
    assert ready["subsystems"]["database"] == "UP"

    full = health_aggregator.get_full_system_status()
    assert full["overall_status"] == "HEALTHY"
