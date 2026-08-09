import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.multiasset.custody_layer import custody_layer

def test_custody_accounts():
    accs = custody_layer.get_custody_accounts()
    assert len(accs) >= 2
    assert accs[0]["custodian"] == "Fireblocks"
