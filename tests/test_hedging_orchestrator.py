import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.multiasset.hedging_orchestrator import hedging_orchestrator

def test_hedging_status():
    st = hedging_orchestrator.get_hedging_status()
    assert st["status"] == "ACTIVE"
    assert "target_delta" in st
