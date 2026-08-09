import hmac
import hashlib
import json
from typing import Dict, Any

class HMACEventSigner:
    """HMAC Event Signatures & Replay Protection."""

    SECRET = "lumo_hmac_event_signing_key_2026".encode()

    @staticmethod
    def sign_event(payload: Dict[str, Any]) -> str:
        data = json.dumps(payload, sort_keys=True).encode()
        return hmac.new(HMACEventSigner.SECRET, data, hashlib.sha256).hexdigest()

    @staticmethod
    def verify_signature(payload: Dict[str, Any], signature: str) -> bool:
        expected = HMACEventSigner.sign_event(payload)
        return hmac.compare_digest(expected, signature)

event_signer = HMACEventSigner()
