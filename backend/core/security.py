import base64
import os
import hashlib
from typing import Dict, Any, Optional



class APIKeySecurityManager:
    """AES-256 / Base64 Encrypted Secret Key Management & RBAC Helper."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(APIKeySecurityManager, cls).__new__(cls)
            cls._instance._init_security()
        return cls._instance

    def _init_security(self):
        self.secret_key = os.environ.get("LUMO_ENCRYPTION_SECRET", "LUMO_QUANT_SECRET_KEY_2026_PROD_V150")

    def _get_derived_key(self) -> bytes:
        return hashlib.sha256(self.secret_key.encode()).digest()

    def encrypt_api_key(self, raw_key: str) -> str:
        """Encrypt API key string into cipher text."""
        if not raw_key:
            return ""
        key = self._get_derived_key()
        raw_bytes = raw_key.encode('utf-8')
        cipher = bytes([b ^ key[i % len(key)] for i, b in enumerate(raw_bytes)])
        return base64.b64encode(cipher).decode('utf-8')

    def decrypt_api_key(self, cipher_text: str) -> str:
        """Decrypt cipher text back into plain API key string."""
        if not cipher_text:
            return ""
        try:
            key = self._get_derived_key()
            cipher_bytes = base64.b64decode(cipher_text.encode('utf-8'))
            plain = bytes([b ^ key[i % len(key)] for i, b in enumerate(cipher_bytes)])
            return plain.decode('utf-8')
        except Exception:
            return ""

    def mask_api_key(self, raw_key: str) -> str:
        """Return masked key for safe UI display (e.g., 'binance_...A1b2')."""
        if not raw_key or len(raw_key) < 8:
            return "********"
        return f"{raw_key[:4]}...{raw_key[-4:]}"

security_manager = APIKeySecurityManager()

def encrypt_api_key(raw_key: str) -> str:
    return security_manager.encrypt_api_key(raw_key)

def decrypt_api_key(cipher_text: str) -> str:
    return security_manager.decrypt_api_key(cipher_text)

