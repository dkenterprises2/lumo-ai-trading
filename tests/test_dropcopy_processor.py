import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_network.compliance.dropcopy_processor import dropcopy_processor

def test_dropcopy_reconciliation():
    res = dropcopy_processor.process_dropcopy_event({"exec_id": "e101"})
    assert res["status"] == "RECONCILED"
    assert "audit_ref" in res
