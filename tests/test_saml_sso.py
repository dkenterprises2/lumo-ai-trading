import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.saml_sso import saml_sso

def test_saml_configuration():
    res = saml_sso.configure_sso("https://idp.test.com", "https://idp.test.com/sso", "CERT")
    assert res["protocol"] == "SAML_2.0"
    assert res["status"] == "CONFIGURED_SIMULATED"
