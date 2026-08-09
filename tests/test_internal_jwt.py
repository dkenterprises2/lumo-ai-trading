import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.security.internal_jwt import internal_jwt_manager
from backend.security.service_auth import service_authenticator

def test_internal_jwt_issuance_and_verification():
    token = internal_jwt_manager.generate_token("trading-service")
    assert isinstance(token, str)

    authed = service_authenticator.authenticate_request("trading-service", token)
    assert authed is True
