import time
import secrets
import hashlib
from typing import Dict, Any, List

class APIKeyManager:
    """API Key Generation, Secret Rotation, & HMAC Authentication Engine."""

    def __init__(self):
        self._keys: List[Dict[str, Any]] = [
            {
                "key_id": "KEY-101",
                "org_id": "ORG-101",
                "name": "Production Trading Key",
                "key_prefix": "lumo_pk_live",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            }
        ]

    def create_api_key(self, org_id: str, name: str) -> Dict[str, Any]:
        """Generate new tenant API key and secret."""
        key_id = f"KEY-{int(time.time())}"
        raw_secret = f"lumo_sk_live_{secrets.token_hex(16)}"
        secret_hash = hashlib.sha256(raw_secret.encode()).hexdigest()

        key_obj = {
            "key_id": key_id,
            "org_id": org_id,
            "name": name,
            "key_prefix": raw_secret[:12],
            "secret_hash": secret_hash,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }
        self._keys.insert(0, key_obj)
        return {
            "key_id": key_id,
            "name": name,
            "api_secret": raw_secret,
            "note": "Store this secret securely. It will not be shown again."
        }

    def list_api_keys(self, org_id: str) -> List[Dict[str, Any]]:
        return [k for k in self._keys if k["org_id"] == org_id]

api_key_manager = APIKeyManager()
