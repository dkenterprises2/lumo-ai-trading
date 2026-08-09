import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.datasets.snapshot_manager import snapshot_manager

def test_reproducibility_check():
    s1 = snapshot_manager.create_snapshot("btc_daily")
    s2 = snapshot_manager.create_snapshot("btc_daily")
    assert s1["checksum"] == s2["checksum"]
