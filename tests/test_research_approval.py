import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.governance.research_approval import research_approval

def test_research_approval():
    res = research_approval.review_approval("APV-901", "APPROVED_FOR_SHADOW")
    assert res["status"] == "APPROVED_FOR_SHADOW"
    assert "audit_trail_ref" in res
