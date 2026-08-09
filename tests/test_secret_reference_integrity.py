import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.platform.vault_service import vault_service

def test_vault_service():
    st = vault_service.get_vault_status()
    assert st["sealed"] is False
    assert "kv-v2" in st["secret_engines"]
