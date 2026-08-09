import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.marketdata.layering_detector import layering_detector

def test_layering_detector_alerts():
    alerts = layering_detector.list_alerts()
    assert len(alerts) >= 1
    assert alerts[0]["severity"] == "CRITICAL"
