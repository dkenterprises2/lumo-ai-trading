import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.research_orchestrator import research_orchestrator

def test_research_orchestrator():
    st = research_orchestrator.get_status()
    assert st["status"] == "OPERATIONAL"
    assert st["active_experiments"] >= 1
