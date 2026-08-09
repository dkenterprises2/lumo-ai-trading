import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.marketdata.spoofing_detector import spoofing_detector

def test_spoofing_detector_alerts():
    alerts = spoofing_detector.list_alerts()
    assert len(alerts) >= 1
    assert alerts[0]["pattern"] == "LARGE_NON_EXECUTING_BID_CANCEL"
