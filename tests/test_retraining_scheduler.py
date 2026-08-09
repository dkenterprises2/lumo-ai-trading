import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.mlops.retraining_scheduler import retraining_scheduler

def test_retraining_scheduler_trigger():
    job = retraining_scheduler.trigger_retraining("DRIFT_TRIGGERED", "MOD-XGB-2026")
    assert job["trigger_type"] == "DRIFT_TRIGGERED"
    assert job["status"] == "IN_PROGRESS"

    jobs = retraining_scheduler.list_jobs()
    assert len(jobs) >= 2
