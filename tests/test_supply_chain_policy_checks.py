import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.platform.supply_chain import supply_chain_security

def test_supply_chain_security():
    scan = supply_chain_security.get_security_scan()
    assert scan["cosign_signed"] is True
    assert scan["vulnerabilities"]["critical"] == 0
