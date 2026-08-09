import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.analytics import saas_analytics

def test_saas_analytics_metrics():
    revenue = saas_analytics.get_revenue_metrics()
    assert revenue["mrr_usd"] > 0
    assert revenue["active_tenants"] > 0

    platform = saas_analytics.get_platform_metrics()
    assert platform["total_tenants"] > 0
