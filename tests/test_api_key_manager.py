import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.api_key_manager import api_key_manager

def test_api_key_generation():
    res = api_key_manager.create_api_key("ORG-101", "Bot Key")
    assert res["key_id"].startswith("KEY-")
    assert res["api_secret"].startswith("lumo_sk_live_")

    keys = api_key_manager.list_api_keys("ORG-101")
    assert len(keys) >= 2
