import time
from typing import Dict, Any, List

class EncryptionKeyRotationManager:
    """Automated Encryption Key Rotation Manager."""

    def __init__(self):
        self._key_versions: List[Dict[str, Any]] = [
            {
                "version_id": "KEY-V1-2026",
                "algorithm": "AES-256-GCM",
                "status": "ACTIVE",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            }
        ]

    def rotate_key(self) -> Dict[str, Any]:
        """Trigger automated encryption key rotation."""
        new_version_id = f"KEY-V{len(self._key_versions)+1}-{int(time.time())}"
        for v in self._key_versions:
            v["status"] = "ARCHIVED"
        
        new_key = {
            "version_id": new_version_id,
            "algorithm": "AES-256-GCM",
            "status": "ACTIVE",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }
        self._key_versions.insert(0, new_key)
        return new_key

    def list_key_versions(self) -> List[Dict[str, Any]]:
        return self._key_versions

key_rotation_manager = EncryptionKeyRotationManager()
