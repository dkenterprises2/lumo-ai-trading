import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_network.tca.slippage_analysis import tca_analytics

def test_implementation_shortfall():
    tca = tca_analytics.calculate_tca("ord_p23_101")
    assert tca["implementation_shortfall_usd"] == 35.2
