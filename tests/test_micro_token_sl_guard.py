import pytest
from ai_strategy import AITradingStrategy
from trader import PaperTrader

def test_ai_strategy_micro_token_precision():
    engine = AITradingStrategy()
    # Test PEPE/USDT micro price ($0.00000268)
    signal = engine.evaluate_trading_signal(
        symbol="PEPE/USDT",
        current_price=0.00000268,
        technical_data={"rsi": 35.0, "atr": 0.00000005, "ema_fast": 0.00000270, "ema_slow": 0.00000260},
        sentiment_summary={"sentiment_score": 65.0, "label": "BULLISH"}
    )
    sl_price = signal["stop_loss_price"]
    # Check that SL is NOT rounded to 0.000100 (which would be 37x higher than entry)
    assert sl_price < 0.00001
    assert sl_price > 0.00000200

@pytest.mark.asyncio
async def test_trader_sl_out_of_bounds_guard():
    trader = PaperTrader(user_id=99999)
    await trader.initialize_and_restore_state()
    await trader.reset_paper_account_async(default_balance=10000.0)

    # Try to open a SHORT position with a bad SL (e.g. 0.000100 for 0.00000268 entry)
    res = trader.open_position(
        symbol="PEPE/USDT",
        side="SHORT",
        price=0.00000268,
        allocation_usd=1000.0,
        stop_loss_price=0.000100,  # Bad SL from old 4-decimal rounding
        take_profit_price=0.00000250,
        leverage=3
    )

    assert res["status"] == "success"
    pos = trader.positions["PEPE/USDT"]
    # The guard must auto-correct SL to ~2.5% above entry (i.e. ~0.00000275), NOT 0.000100!
    assert pos["stop_loss_price"] < 0.00001

@pytest.mark.asyncio
async def test_trader_isolated_margin_loss_cap():
    trader = PaperTrader(user_id=99999)
    await trader.initialize_and_restore_state()
    await trader.reset_paper_account_async(default_balance=10000.0)

    trader.open_position(
        symbol="SHIB/USDT",
        side="SHORT",
        price=0.00000457,
        allocation_usd=1000.0,
        stop_loss_price=0.00000468,
        take_profit_price=0.00000430,
        leverage=3
    )

    # Close position at an extreme bad exit price 0.000100
    res = trader.close_position(
        symbol="SHIB/USDT",
        price=0.000100,
        reason="Test Close"
    )

    assert res["status"] == "success"
    # Trade history must cap loss at 100% of margin
    closed_trade = trader.trade_history[0]
    assert closed_trade["pnl_pct"] == -100.0
