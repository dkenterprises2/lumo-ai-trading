import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.platform.health_service import health_service

def test_health_probes():
    h = health_service.get_health()
    assert h["status"] == "UP"
    dh = health_service.get_deep_health()
    assert dh["database"] == "CONNECTED"
