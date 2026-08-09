import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.multiasset.yield_router import yield_router

def test_yield_opportunities():
    opps = yield_router.get_yield_opportunities()
    assert len(opps) >= 1
    assert opps[0]["apy"] > 0
