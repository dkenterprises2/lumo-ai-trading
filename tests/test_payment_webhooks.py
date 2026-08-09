import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.payment_webhooks import payment_webhook_handler

def test_stripe_webhook_processing():
    res = payment_webhook_handler.process_webhook("customer.subscription.updated", {"id": "sub_123"})
    assert res["processed"] is True
    assert res["status"] == "SUCCESS"
