import hashlib
from typing import Dict, Any

class TamperEvidentHasher:
    """Tamper-Evident SHA-256 Hashing verification tool."""

    @staticmethod
    def compute_hash(data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    def verify_hash(data: str, expected_hash: str) -> bool:
        return hashlib.sha256(data.encode()).hexdigest() == expected_hash

tamper_evident_hasher = TamperEvidentHasher()
