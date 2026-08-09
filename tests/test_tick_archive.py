import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.marketdata.tick_archive import tick_archive

def test_tick_archive():
    res = tick_archive.archive_ticks("BTC/USDT")
    assert res["status"] == "SUCCESS"
    assert res["archived_rows"] > 0
