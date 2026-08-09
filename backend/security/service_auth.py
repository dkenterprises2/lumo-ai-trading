from typing import Dict, Any
from backend.security.internal_jwt import internal_jwt_manager

class InterServiceAuthenticator:
    """mTLS-ready Configuration Abstraction & Identity Headers."""

    @staticmethod
    def authenticate_request(service_name: str, auth_token: str) -> bool:
        try:
            payload = internal_jwt_manager.verify_token(auth_token)
            return payload.get("sub") == service_name
        except Exception:
            return False

service_authenticator = InterServiceAuthenticator()
