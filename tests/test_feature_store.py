import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.mlops.feature_store import feature_store_manager

def test_feature_store_versioning():
    version = feature_store_manager.register_feature_version("New Feature Set", ["rsi_14", "volatility"], "2.0.0")
    assert version["version"] == "2.0.0"
    assert version["is_immutable"] is True

    versions = feature_store_manager.list_feature_versions()
    assert len(versions) >= 2
