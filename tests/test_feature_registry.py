import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.feature_store.feature_registry import feature_registry

def test_feature_registry():
    feats = feature_registry.list_features()
    assert len(feats) >= 1
    m = feature_registry.materialize("momentum_20d")
    assert m["status"] == "MATERIALIZED"
