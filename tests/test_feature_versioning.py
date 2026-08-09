import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.feature_store.feature_registry import feature_registry

def test_feature_versioning():
    f = feature_registry.get_feature("momentum_20d")
    assert f["version"] == "v1"
