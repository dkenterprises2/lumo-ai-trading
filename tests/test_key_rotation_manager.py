import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.security.key_rotation_manager import key_rotation_manager

def test_key_rotation_manager():
    rotated = key_rotation_manager.rotate_key()
    assert rotated["status"] == "ACTIVE"

    keys = key_rotation_manager.list_key_versions()
    assert len(keys) >= 2
