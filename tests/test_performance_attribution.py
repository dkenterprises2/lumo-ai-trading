import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.performance_attribution import performance_attribution

def test_performance_attribution():
    attr = performance_attribution.get_attribution()
    assert "total_alpha" in attr
    assert attr["total_alpha"] > 0
