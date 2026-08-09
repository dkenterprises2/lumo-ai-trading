import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai.research_workspace import research_workspace_manager

def test_dataset_catalog():
    catalog = research_workspace_manager.list_dataset_catalog()
    assert len(catalog) >= 4
    types = [d["type"] for d in catalog]
    assert "OHLCV" in types
    assert "SENTIMENT" in types
