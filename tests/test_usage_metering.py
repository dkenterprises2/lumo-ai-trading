import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.usage_metering import usage_metering

def test_usage_metering():
    usage_metering.record_usage("api_calls", 5)
    data = usage_metering.get_usage()
    assert data["api_calls"] >= 5
