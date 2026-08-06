import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.exchange.exchange_manager import LeakyBucketRateLimiter

def test_rate_limiter_leaky_bucket():
    limiter = LeakyBucketRateLimiter(requests_per_minute=60)
    acquired = limiter.acquire()
    assert acquired is True
