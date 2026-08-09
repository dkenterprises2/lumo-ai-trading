import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.security.incident_manager import security_incident_manager

def test_security_incident_creation():
    inc = security_incident_manager.create_incident("Suspicious IP Access", "HIGH")
    assert inc["incident_id"].startswith("INC-")
    assert inc["severity"] == "HIGH"
