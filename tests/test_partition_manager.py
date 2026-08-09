import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.data_lake.parquet_store import parquet_store

def test_partition_pruning():
    parts = parquet_store.list_partitions("market_data")
    assert any("symbol=BTCUSDT" in p for p in parts)
