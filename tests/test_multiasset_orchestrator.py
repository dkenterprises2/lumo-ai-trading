import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.multiasset.multiasset_orchestrator import multiasset_orchestrator

def test_multiasset_orchestrator():
    st = multiasset_orchestrator.get_status()
    assert st["status"] == "OPERATIONAL"
    assert len(st["active_gateways"]) == 5
