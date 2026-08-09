import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.compute.distributed_scheduler import distributed_scheduler

def test_distributed_scheduler():
    job = distributed_scheduler.submit_job("parameter_sweep")
    assert job["status"] == "QUEUED_SIMULATED"
    assert job["allocated_cores"] == 16
