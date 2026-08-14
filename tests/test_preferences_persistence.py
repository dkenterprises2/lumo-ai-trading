import pytest
import asyncio
from backend.repositories.trader_repository import TraderRepository
from trader import PaperTrader

@pytest.mark.asyncio
async def test_trading_preferences_persistence_roundtrip():
    repo = TraderRepository()
    test_user_id = 99999

    # Save preferences to DB
    await repo.save_portfolio_state(
        usdt_balance=15000.0,
        initial_balance=10000.0,
        margin_used=2000.0,
        total_value=17000.0,
        auto_bot_enabled=True,
        active_strategy="AI Hybrid",
        risk_mode="AGGRESSIVE",
        default_allocation_usd=5000.0,
        default_leverage=3,
        max_concurrent_trades=50,
        max_capital_per_trade_pct=10.0,
        daily_loss_limit_pct=5.0,
        symbol_cooldown_minutes=0,
        allowed_symbols=["BTC/USDT", "ETH/USDT", "SOL/USDT"],
        user_id=test_user_id
    )

    # Reload trader instance from DB
    trader = PaperTrader(user_id=test_user_id)
    await trader.initialize_and_restore_state()

    # Assert that all saved preferences persist cleanly
    assert trader.usdt_balance == 15000.0
    assert trader.default_allocation_usd == 5000.0
    assert trader.default_leverage == 3
    assert trader.max_open_positions == 50
    assert trader.max_capital_per_trade_pct == 10.0
    assert trader.risk_manager.config.max_concurrent_trades == 50
    assert trader.risk_manager.config.max_daily_loss_pct == 5.0
    assert trader.symbol_cooldown_minutes == 0
    assert trader.allowed_symbols == ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
