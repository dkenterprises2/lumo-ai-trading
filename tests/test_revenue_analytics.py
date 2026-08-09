import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.admin.revenue_analytics import platform_revenue_analytics

def test_platform_revenue_analytics():
    revenue = platform_revenue_analytics.get_revenue_summary()
    assert revenue["mrr_usd"] > 0
    assert revenue["arr_usd"] > 0
    assert "subscriptions_by_plan" in revenue
