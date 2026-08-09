import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.security.event_signing import event_signer

def test_hmac_event_signing():
    payload = {"event_id": "EVT-1", "action": "ORDER_FILLED"}
    sig = event_signer.sign_event(payload)
    assert isinstance(sig, str)
    assert event_signer.verify_signature(payload, sig) is True
