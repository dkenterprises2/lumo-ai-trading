import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.branding_service import branding_service

def test_branding_customization():
    b = branding_service.get_branding()
    assert b["app_name"] == "Lumo Pro"
    up = branding_service.update_branding({"app_name": "Custom Trading Desk"})
    assert up["app_name"] == "Custom Trading Desk"
