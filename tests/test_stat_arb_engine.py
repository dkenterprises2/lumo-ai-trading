import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.stat_arb_engine import stat_arb_engine

def test_stat_arb_engine_scan():
    pairs = stat_arb_engine.scan_pairs()
    assert len(pairs) >= 2
    assert pairs[0]["pair_id"] == "PAIR-BTC-ETH"
