import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.webhook_service import tenant_webhook_service

def test_webhook_endpoints():
    whs = tenant_webhook_service.list_webhooks()
    assert len(whs) >= 1
    w = tenant_webhook_service.create_webhook("https://hooks.slack.com/test", ["order_filled"])
    assert w["webhook_id"].startswith("wh_")
