import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.compliance.regulatory_reporting import regulatory_reporting_engine

def test_regulatory_reporting_generation():
    rep = regulatory_reporting_engine.generate_report("DAILY_TRADING_ACTIVITY", "ORG-101")
    assert rep["report_id"].startswith("REP-")
    assert rep["status"] == "COMPLETED"
    assert "CSV" in rep["formats_available"]
