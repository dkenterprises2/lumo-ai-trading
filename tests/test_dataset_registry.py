import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.datasets.snapshot_manager import snapshot_manager

def test_dataset_snapshot():
    snap = snapshot_manager.create_snapshot("market_data")
    assert snap["status"] == "IMMUTABLE_CREATED"
    assert snap["row_count"] > 0
