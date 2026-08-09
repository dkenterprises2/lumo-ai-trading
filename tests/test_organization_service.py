import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.organization_service import organization_service

def test_organization_creation():
    org = organization_service.create_organization("Beta Hedge", "beta-hedge", "owner@beta.com")
    assert org["org_id"] == "org_beta-hedge"
    assert len(organization_service.list_organizations()) >= 2
