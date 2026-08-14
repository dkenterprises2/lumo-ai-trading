import pytest
from backend.portfolio_risk.exposure_allocator import ExposureAllocator

def test_exposure_allocation():
    allocator = ExposureAllocator()
    res = allocator.allocate_exposure(10000.0)

    assert "AI Hybrid" in res
    assert "Scalping" in res
    assert "Stat Arb" in res
    total_alloc = sum(a.allocated_usd for a in res.values())
    assert abs(total_alloc - 10000.0) < 1.0
