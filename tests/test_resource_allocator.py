import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.compute.distributed_scheduler import distributed_scheduler

def test_resource_allocation():
    job = distributed_scheduler.submit_job("rl_training")
    assert "allocated_gpu" in job
