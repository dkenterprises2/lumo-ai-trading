import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.security.tamper_evident_hashing import tamper_evident_hasher

def test_tamper_evident_hashing():
    data = "immutable_audit_data_string"
    h = tamper_evident_hasher.compute_hash(data)
    assert isinstance(h, str)
    assert tamper_evident_hasher.verify_hash(data, h) is True
