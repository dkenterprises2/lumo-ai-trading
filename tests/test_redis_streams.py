import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.infrastructure.redis_streams import redis_streams_manager

def test_redis_pubsub_streams():
    pub = redis_streams_manager.publish_event("system_health", {"status": "OK"})
    assert pub["status"] == "DELIVERED"
    assert pub["subscribers_notified"] > 0

    cluster = redis_streams_manager.get_cluster_status()
    assert cluster["cluster_status"] == "HEALTHY"
    assert cluster["active_channels"] >= 4
