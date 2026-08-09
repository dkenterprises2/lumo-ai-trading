import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.datasets.snapshot_manager import snapshot_manager

def test_snapshot_checksum():
    snap = snapshot_manager.create_snapshot("ticks")
    assert snap["checksum"].startswith("sha256:")
