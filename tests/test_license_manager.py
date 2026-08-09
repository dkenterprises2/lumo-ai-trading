import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.license_manager import license_manager

def test_license_manager():
    lic = license_manager.validate_license("KEY-101")
    assert lic["status"] == "VALID"
    assert lic["tier"] == "ENTERPRISE"
