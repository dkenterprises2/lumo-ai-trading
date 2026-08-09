import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_network.tca.slippage_analysis import tca_analytics

def test_slippage_analysis():
    tca = tca_analytics.calculate_tca("ord_p23_101")
    assert tca["status"] == "COMPUTED"
    assert tca["arrival_price_slippage_bps"] == 1.4
