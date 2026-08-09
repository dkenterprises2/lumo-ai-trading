import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.compliance.data_retention import data_retention_policy_manager

def test_data_retention_policies():
    policies = data_retention_policy_manager.list_policies()
    assert len(policies) == 3
    assert policies[0]["retention_years"] == 7
