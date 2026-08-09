import time
import json
import base64
import hmac
import hashlib
from typing import Dict, Any

class InternalJWTManager:
    """Signed Internal JWT Tokens for Inter-Service Authorization."""

    SECRET_KEY = "lumo_internal_microservices_signing_secret_2026".encode()

    @staticmethod
    def _b64url_encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

    @staticmethod
    def _b64url_decode(data: str) -> bytes:
        padding = '=' * (4 - (len(data) % 4))
        return base64.urlsafe_b64encode(base64.urlsafe_b64decode((data + padding).encode()))

    @staticmethod
    def generate_token(service_name: str, valid_seconds: int = 300) -> str:
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "iss": "lumo-auth-service",
            "sub": service_name,
            "iat": int(time.time()),
            "exp": int(time.time()) + valid_seconds
        }
        
        hdr_b64 = InternalJWTManager._b64url_encode(json.dumps(header).encode())
        payload_b64 = InternalJWTManager._b64url_encode(json.dumps(payload).encode())
        
        signing_input = f"{hdr_b64}.{payload_b64}".encode()
        sig = hmac.new(InternalJWTManager.SECRET_KEY, signing_input, hashlib.sha256).digest()
        sig_b64 = InternalJWTManager._b64url_encode(sig)
        
        return f"{hdr_b64}.{payload_b64}.{sig_b64}"

    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid JWT format")
        
        hdr_b64, payload_b64, sig_b64 = parts
        signing_input = f"{hdr_b64}.{payload_b64}".encode()
        expected_sig = InternalJWTManager._b64url_encode(
            hmac.new(InternalJWTManager.SECRET_KEY, signing_input, hashlib.sha256).digest()
        )
        
        if not hmac.compare_digest(expected_sig, sig_b64):
            raise ValueError("Invalid signature")
        
        payload_json = base64.urlsafe_b64decode((payload_b64 + '=' * (4 - (len(payload_b64) % 4))).encode()).decode()
        payload = json.loads(payload_json)
        
        if payload.get("exp", 0) < time.time():
            raise ValueError("Token expired")
        
        return payload

internal_jwt_manager = InternalJWTManager()
