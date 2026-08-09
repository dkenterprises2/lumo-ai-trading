import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.multiasset.security_master import security_master

def test_security_master():
    sec = security_master.list_securities()
    assert len(sec) >= 2
    assert sec[0]["asset_id"] == "BTCUSDT"
