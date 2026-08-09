import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.compliance.audit_ledger import audit_ledger

def test_audit_ledger_append_and_integrity():
    entry = audit_ledger.append_entry(1, "ORG-101", "ORDER_SUBMITTED", "ORDER", "ORD-999")
    assert entry["entry_id"].startswith("AUD-")
    assert audit_ledger.verify_integrity() is True
