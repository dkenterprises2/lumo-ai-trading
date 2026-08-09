import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_algos.order_slicing_policies import order_slicing_policies

def test_order_slicing_policies():
    policies = order_slicing_policies.list_policies()
    assert len(policies) == 2
    assert policies[0]["status"] == "ACTIVE"
