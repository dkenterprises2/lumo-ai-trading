import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.api_key_service import api_key_service

def test_api_key_lifecycle():
    keys = api_key_service.list_keys()
    assert len(keys) >= 1
    k = api_key_service.create_key("Bot Key", ["marketdata:read"])
    assert k["raw_secret"].startswith("lumo_live_")
    rot = api_key_service.rotate_key(k["key_id"])
    assert "raw_secret" in rot
