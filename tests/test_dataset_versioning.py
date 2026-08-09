import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.dataset_versioning import dataset_versioning

def test_dataset_versioning():
    ds = dataset_versioning.register_dataset("ETH/USDT", "15m", 35000)
    assert ds["dataset_id"].startswith("DS-")
    assert len(dataset_versioning.list_datasets()) >= 2
