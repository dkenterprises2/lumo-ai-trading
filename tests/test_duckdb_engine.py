import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.data_lake.duckdb_engine import duckdb_engine

def test_duckdb_engine():
    res = duckdb_engine.execute_query("SELECT * FROM market_data")
    assert len(res) >= 1
    assert "close" in res[0]
