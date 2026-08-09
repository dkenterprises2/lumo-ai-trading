import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.platform.chaos_engine import chaos_engine

def test_chaos_safety_override():
    prod = chaos_engine.run_experiment("pod_kill", "prod")
    assert prod["status"] == "BLOCKED_SAFETY_OVERRIDE_REQUIRED"

    stg = chaos_engine.run_experiment("pod_kill", "staging")
    assert stg["status"] == "PASSED_SUCCESSFULLY"
