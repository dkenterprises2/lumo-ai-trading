import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.discovery.service_registry import service_registry
from backend.discovery.load_balancer import load_balancer

def test_service_registry_and_lb():
    inst = service_registry.register_service("test-svc", "test-1", "10.0.0.1", 8000)
    assert inst["status"] == "UP"

    selected = load_balancer.select_instance("test-svc")
    assert selected is not None
    assert selected["id"] == "test-1"
