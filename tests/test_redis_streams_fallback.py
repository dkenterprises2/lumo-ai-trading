import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.eventbus.redis_streams_bus import redis_streams_bus
from backend.eventbus.contracts import DriftDetectedEvent

def test_redis_streams_fallback():
    evt = DriftDetectedEvent(event_id="EVT-DRIFT-1", psi_score=0.14, model_id="MOD-XGB-2026")
    assert redis_streams_bus.publish("mlops.drift", evt) is True
