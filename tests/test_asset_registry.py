import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.multiasset.asset_registry import asset_registry

def test_asset_registry_classes():
    cls = asset_registry.get_supported_classes()
    assert "EQUITY" in cls
    assert "CRYPTO" in cls
