import pytest
from backend.safety.paper_mode_guard import PaperTradingGuard, PaperTradingViolation

def test_paper_guard_blocks_real_order():
    guard = PaperTradingGuard(paper_mode=True)
    with pytest.raises(PaperTradingViolation):
        guard.block_live_exchange_order("BINANCE", "BTC/USDT", 1.0)

def test_paper_guard_blocks_withdrawal():
    guard = PaperTradingGuard(paper_mode=True)
    with pytest.raises(PaperTradingViolation):
        guard.block_withdrawal("USDT", 500.0, "0x123456789")

def test_paper_guard_blocks_api_key_usage():
    guard = PaperTradingGuard(paper_mode=True)
    with pytest.raises(PaperTradingViolation):
        guard.block_live_api_key_usage("secret_key_123")

def test_paper_guard_assertion_passes():
    guard = PaperTradingGuard(paper_mode=True)
    guard.assert_paper_mode("Paper Mode Check")
    assert guard.paper_mode is True
