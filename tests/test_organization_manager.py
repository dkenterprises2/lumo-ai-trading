import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.organization_manager import organization_manager

def test_organization_manager_crud():
    org = organization_manager.create_organization("Beta Capital", owner_id=2)
    assert org["org_id"].startswith("ORG-")
    assert org["slug"] == "beta-capital"

    fetched = organization_manager.get_organization(org["org_id"])
    assert fetched["name"] == "Beta Capital"
