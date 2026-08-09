import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.oauth_microsoft import oauth_microsoft

def test_microsoft_oauth():
    url = oauth_microsoft.get_auth_url()
    assert url["provider"] == "MICROSOFT_ENTRA"
    assert "login.microsoftonline.com" in url["auth_url"]
