import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_network.fix.fix_gateway import fix_gateway

def test_fix_sequence_recovery():
    res = fix_gateway.recover_session("sess_01")
    assert res["last_seq_no"] == 1420
