import time, secrets
from typing import Dict, Any, List

class APIKeyService:
    """Scoped API Keys, Secret Rotation & Developer App Credentials Manager."""

    def __init__(self):
        self._keys: List[Dict[str, Any]] = [
            {
                "key_id": "key_live_991",
                "name": "Production Trading Bot",
                "prefix": "lumo_live_x88",
                "scopes": ["marketdata:read", "execution:write", "ai:manage"],
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                "status": "ACTIVE"
            }
        ]

    def list_keys(self) -> List[Dict[str, Any]]:
        return self._keys

    def create_key(self, name: str, scopes: List[str]) -> Dict[str, Any]:
        raw_secret = f"lumo_live_{secrets.token_hex(16)}"
        item = {
            "key_id": f"key_live_{int(time.time())}",
            "name": name,
            "prefix": raw_secret[:12],
            "raw_secret": raw_secret,
            "scopes": scopes,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "status": "ACTIVE"
        }
        self._keys.append(item)
        return item

    def rotate_key(self, key_id: str) -> Dict[str, Any]:
        for k in self._keys:
            if k["key_id"] == key_id:
                new_secret = f"lumo_live_{secrets.token_hex(16)}"
                k["prefix"] = new_secret[:12]
                k["raw_secret"] = new_secret
                return k
        return {"key_id": key_id, "status": "NOT_FOUND"}

api_key_service = APIKeyService()
