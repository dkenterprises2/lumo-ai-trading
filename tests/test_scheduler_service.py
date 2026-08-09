import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.shared.health import get_service_health

def test_scheduler_service_health():
    health = get_service_health("scheduler-service")
    assert health["service"] == "scheduler-service"
    assert health["status"] == "HEALTHY"
