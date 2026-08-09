import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.multiasset.settlement_engine import settlement_engine

def test_settlement_instruction():
    inst = settlement_engine.create_instruction("USDT", 100000.0, "Binance Custody")
    assert inst["instruction_id"].startswith("SETTLE-INST-")
    assert inst["status"] == "SETTLED_SIMULATED"
