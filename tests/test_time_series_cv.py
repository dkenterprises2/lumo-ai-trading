import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.time_series_cv import time_series_cv

def test_time_series_cv():
    splits = time_series_cv.get_split_indices(1000, 5)
    assert len(splits) == 5
    assert splits[0]["fold"] == 1
