import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.multiasset.unified_portfolio import unified_portfolio

def test_unified_nav():
    nav = unified_portfolio.calculate_global_nav("USD")
    assert nav["global_nav_usd"] > 0
    assert nav["cefi_total_usd"] > 0
    assert nav["defi_total_usd"] > 0
