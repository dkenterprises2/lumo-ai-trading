import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.feature_flags import feature_flags

def test_feature_flags():
    assert feature_flags.is_enabled("white_label") is True
    res = feature_flags.set_flag("experimental_algo", True)
    assert res["enabled"] is True
    assert feature_flags.is_enabled("experimental_algo") is True
