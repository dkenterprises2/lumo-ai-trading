import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.multiasset.treasury_manager import treasury_manager

def test_treasury_status():
    st = treasury_manager.get_treasury_status()
    assert st["total_treasury_usd"] > 0
    assert st["avg_yield_apy"] > 0
