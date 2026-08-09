import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_algos.iceberg_engine import iceberg_engine

def test_iceberg_hidden_reserve():
    res = iceberg_engine.initialize_iceberg(50.0, 5.0)
    assert res["visible_display_quantity"] == 5.0
    assert res["hidden_reserve_quantity"] == 45.0
