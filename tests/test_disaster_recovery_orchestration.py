import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.platform.platform_orchestrator import platform_orchestrator

def test_platform_orchestration():
    st = platform_orchestrator.get_status()
    assert st["status"] == "OPERATIONAL"
    assert len(st["clusters"]) == 2
