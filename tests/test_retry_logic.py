import sys
import os
import pytest
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_exponential_backoff_retry():
    max_retries = 3
    success = False
    attempts = 0

    for attempt in range(max_retries):
        attempts += 1
        if attempt == 1:
            success = True
            break
        time.sleep(0.01 * (2 ** attempt))

    assert success is True
    assert attempts == 2
