import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.multiasset.margin_engine import margin_engine

def test_margin_engine():
    st = margin_engine.get_margin_status()
    assert "initial_margin_usd" in st
    assert st["margin_health"] == "SAFE"
