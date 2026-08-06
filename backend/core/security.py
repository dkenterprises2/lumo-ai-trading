import os
import base64
import json
import time
import hmac
import hashlib
import secrets
from typing import Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from cryptography.fernet import Fernet
from backend.core.config import settings
from backend.core.logger import logger

# Initialize Cryptographic Fernet Suite for Exchange API Key Protection
def _get_fernet_instance() -> Fernet:
    """Generate or parse 32-byte urlsafe base64 Fernet key."""
    raw_key = settings.ENCRYPTION_KEY
    try:
        # Ensure key is valid 32-byte base64
        key_bytes = base64.urlsafe_b64encode(hashlib.sha256(raw_key.encode()).digest())
        return Fernet(key_bytes)
    except Exception as e:
        logger.error(f"Error initializing Fernet encryption suite: {e}")
        # Fallback deterministic key from secret_key
        fallback_bytes = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode()).digest())
        return Fernet(fallback_bytes)

fernet = _get_fernet_instance()

# ----------------------------------------------------
# 1. Password Hashing (PBKDF2 HMAC SHA-256)
# ----------------------------------------------------

def hash_password(password: str) -> str:
    """Hash password using PBKDF2 HMAC SHA-256 with 100,000 iterations and salt."""
    if not password:
        raise ValueError("Password cannot be empty")
    salt = secrets.token_bytes(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    storage = salt + key
    return base64.b64encode(storage).decode('ascii')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against PBKDF2 HMAC SHA-256 hash."""
    if not plain_password or not hashed_password:
        return False
    try:
        decoded = base64.b64decode(hashed_password.encode('ascii'))
        salt = decoded[:16]
        stored_key = decoded[16:]
        new_key = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, 100000)
        return hmac.compare_digest(stored_key, new_key)
    except Exception as e:
        logger.warning(f"Password verification failed with exception: {e}")
        return False

# ----------------------------------------------------
# 2. JWT Authentication Tokens (HMAC SHA-256)
# ----------------------------------------------------

def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')

def _base64url_decode(data: str) -> bytes:
    padding = '=' * (4 - (len(data) % 4))
    return base64.urlsafe_b64encode(base64.urlsafe_b64decode(data + padding))

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create signed JWT token with claims and expiration."""
    to_encode = data.copy()
    now_utc = datetime.now(timezone.utc)
    if expires_delta:
        expire = now_utc + expires_delta
    else:
        expire = now_utc + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": int(expire.timestamp()), "iat": int(now_utc.timestamp())})

    header = {"alg": settings.JWT_ALGORITHM, "typ": "JWT"}
    header_json = json.dumps(header, separators=(',', ':')).encode('utf-8')
    payload_json = json.dumps(to_encode, separators=(',', ':')).encode('utf-8')

    encoded_header = _base64url_encode(header_json)
    encoded_payload = _base64url_encode(payload_json)

    signing_input = f"{encoded_header}.{encoded_payload}".encode('utf-8')
    signature = hmac.new(settings.SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
    encoded_signature = _base64url_encode(signature)

    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify signature and expiration of JWT token."""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None

        encoded_header, encoded_payload, encoded_signature = parts
        signing_input = f"{encoded_header}.{encoded_payload}".encode('utf-8')
        expected_sig = hmac.new(settings.SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
        actual_sig = base64.urlsafe_b64decode(encoded_signature + '=' * (4 - (len(encoded_signature) % 4)))

        if not hmac.compare_digest(expected_sig, actual_sig):
            logger.warning("JWT signature mismatch")
            return None

        payload_bytes = base64.urlsafe_b64decode(encoded_payload + '=' * (4 - (len(encoded_payload) % 4)))
        payload = json.loads(payload_bytes.decode('utf-8'))

        exp = payload.get("exp")
        if exp and int(time.time()) > exp:
            logger.warning("JWT token expired")
            return None

        return payload
    except Exception as e:
        logger.error(f"JWT verification error: {e}")
        return None

# ----------------------------------------------------
# 3. Exchange API Key Encryption & Decryption
# ----------------------------------------------------

def encrypt_api_key(plain_api_key: str) -> str:
    """Encrypt exchange API key/secret using AES-256 Fernet."""
    if not plain_api_key:
        return ""
    encrypted_bytes = fernet.encrypt(plain_api_key.encode('utf-8'))
    return encrypted_bytes.decode('utf-8')

def decrypt_api_key(cipher_api_key: str) -> str:
    """Decrypt exchange API key/secret using AES-256 Fernet."""
    if not cipher_api_key:
        return ""
    try:
        decrypted_bytes = fernet.decrypt(cipher_api_key.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to decrypt API Key: {e}")
        raise ValueError("Decryption failed: Invalid cipher text or key")

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "verify_token",
    "encrypt_api_key",
    "decrypt_api_key"
]
