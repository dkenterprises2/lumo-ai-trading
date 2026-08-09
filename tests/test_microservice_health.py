import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.shared.health import get_service_health

def test_all_microservices_health():
    services = ["api-gateway", "trading-service", "execution-service", "ai-inference-service", "websocket-gateway"]
    for s in services:
        h = get_service_health(s)
        assert h["status"] == "HEALTHY"
