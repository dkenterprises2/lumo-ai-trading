import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_algos.execution_orchestrator import execution_orchestrator

def test_execution_orchestrator():
    st = execution_orchestrator.get_status()
    assert st["status"] == "OPERATIONAL"
    assert "TWAP" in st["supported_algos"]
