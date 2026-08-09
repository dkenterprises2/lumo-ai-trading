import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.platform.dr_runbooks import dr_runbooks

def test_runbook_dry_run():
    res = dr_runbooks.execute_dry_run("database_failover")
    assert res["dry_run_status"] == "PASSED_SIMULATED"
    assert res["steps_executed"] == 6
