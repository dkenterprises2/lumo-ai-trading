import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_network.environment.environment_manager import environment_manager

def test_environment_manager():
    curr = environment_manager.get_current_environment()
    assert curr["environment"] == "PAPER"
    sw = environment_manager.request_switch("SHADOW")
    assert sw["switched"] is True
