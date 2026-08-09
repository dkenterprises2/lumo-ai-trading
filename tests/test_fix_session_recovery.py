import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_network.fix.fix_gateway import fix_gateway

def test_session_recovery():
    res = fix_gateway.recover_session("sess_02")
    assert res["status"] == "RECOVERED"
