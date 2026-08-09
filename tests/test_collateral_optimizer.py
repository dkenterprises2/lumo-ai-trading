import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.multiasset.collateral_optimizer import collateral_optimizer

def test_collateral_optimization():
    res = collateral_optimizer.optimize_collateral(1000000.0, 400000.0)
    assert res["free_collateral_usd"] == 600000.0
    assert res["utilization_ratio_pct"] == 40.0
