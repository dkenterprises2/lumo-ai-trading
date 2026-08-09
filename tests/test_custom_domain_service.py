import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.custom_domain_service import custom_domain_service

def test_custom_domain_registration():
    doms = custom_domain_service.list_domains()
    assert len(doms) >= 1
    new_d = custom_domain_service.register_domain("trade.beta.com", "org_beta")
    assert new_d["domain"] == "trade.beta.com"
