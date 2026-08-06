import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.exchange.okx_adapter import OKXAdapter
from backend.exchange.paper_adapter import PaperExchangeAdapter

def test_position_synchronization():
    okx = OKXAdapter(testnet=True)
    pos = okx.fetch_positions()
    assert isinstance(pos, dict)

    paper = PaperExchangeAdapter()
    paper_pos = paper.fetch_positions()
    assert isinstance(paper_pos, dict)
