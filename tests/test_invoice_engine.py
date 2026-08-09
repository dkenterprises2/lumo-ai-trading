import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.invoice_engine import invoice_engine

def test_invoice_engine_listing():
    invoices = invoice_engine.list_invoices("ORG-101")
    assert len(invoices) >= 1
    assert invoices[0]["status"] == "PAID"
