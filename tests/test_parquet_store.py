import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.data_lake.parquet_store import parquet_store

def test_parquet_store():
    parts = parquet_store.list_partitions("market_data")
    assert len(parts) >= 1
    stats = parquet_store.get_stats()
    assert stats["compression"] == "ZSTD"
