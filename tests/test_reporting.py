import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.analytics.reporting_engine import reporting_engine

def test_reporting_engine_generation_and_export():
    daily_rep = reporting_engine.generate_report("DAILY", user_id=1)
    assert daily_rep["period"] == "DAILY"
    assert daily_rep["risk_status"] == "APPROVED_COMPLIANT"

    monthly_rep = reporting_engine.generate_report("MONTHLY", user_id=1)
    assert monthly_rep["period"] == "MONTHLY"

    csv_out = reporting_engine.export_report_csv(daily_rep)
    assert "Metric,Value" in csv_out
    assert "sharpe_ratio" in csv_out
