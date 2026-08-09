import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.discovery.heartbeat_manager import heartbeat_manager
from backend.discovery.service_registry import service_registry

def test_service_eviction_failover():
    evicted = heartbeat_manager.run_eviction_pass()
    assert isinstance(evicted, int)
