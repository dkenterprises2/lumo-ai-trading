import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.infrastructure.disaster_recovery import disaster_recovery_manager

def test_disaster_recovery_simulation():
    res = disaster_recovery_manager.execute_recovery_test()
    assert res["status"] == "RECOVERY_TEST_SUCCESSFUL"
    assert "rpo" in res["recovery_point_objective_rpo"].lower() or "seconds" in res["recovery_point_objective_rpo"]
    assert res["restored_tables_count"] > 0
