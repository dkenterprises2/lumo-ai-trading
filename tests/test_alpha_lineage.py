import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.alpha_factory.lineage.alpha_lineage import alpha_lineage_tracker

def test_alpha_lineage():
    lin = alpha_lineage_tracker.get_lineage("alpha_momentum_v12")
    assert lin["provenance_verified"] is True
    assert lin["dataset_snapshot_id"] == "snap_2026_08_09_BTC"
