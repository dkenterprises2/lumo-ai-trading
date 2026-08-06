import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.security import security_manager

def test_api_key_encryption_decryption():
    raw_key = "binance_api_key_secret_12345"
    enc_key = security_manager.encrypt_api_key(raw_key)

    assert enc_key != raw_key
    dec_key = security_manager.decrypt_api_key(enc_key)
    assert dec_key == raw_key

    masked = security_manager.mask_api_key(raw_key)
    assert "bina...2345" in masked or "..." in masked
