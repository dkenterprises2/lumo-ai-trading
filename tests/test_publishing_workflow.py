import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.alpha_factory.marketplace.strategy_catalog import strategy_catalog

def test_publishing_workflow():
    pub = strategy_catalog.publish_strategy("alpha_test")
    assert pub["certification"] == "PASSED"
