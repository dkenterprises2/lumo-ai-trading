import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.oauth_google import oauth_google

def test_google_oauth():
    url = oauth_google.get_auth_url()
    assert url["provider"] == "GOOGLE"
    assert "accounts.google.com" in url["auth_url"]
