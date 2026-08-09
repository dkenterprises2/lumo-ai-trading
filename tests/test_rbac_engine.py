import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.rbac_engine import rbac_engine

def test_rbac_declarative_evaluation():
    assert rbac_engine.evaluate_permission("SUPER_ADMIN", "anything", "any") is True
    assert rbac_engine.evaluate_permission("TRADER", "execution.orders", "create") is True
    assert rbac_engine.evaluate_permission("VIEWER", "execution.orders", "create") is False
