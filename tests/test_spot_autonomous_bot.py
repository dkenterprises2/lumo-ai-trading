"""
Unit & Integration Tests for Spot Autonomous Self-Learning Bot and Isolated Sub-Wallet.
"""

import pytest
import time
from backend.spot_research.spot_sub_wallet import SpotSubWalletManager, SpotWalletState
from backend.spot_research.spot_autonomous_bot import SpotAutonomousBot, SpotBotConfig
from backend.spot_research.coin_discovery_engine import DiscoveredCoin
from backend.spot_research.coin_classifier import CoinClassifier
from backend.spot_research.coin_risk_engine import CoinRiskEngine
from backend.spot_research.coin_ai_researcher import CoinAIResearcher
from backend.spot_research.paper_validation_engine import PaperValidationEngine

def test_spot_sub_wallet_margin_and_pnl(tmp_path):
    db_file = str(tmp_path / "test_spot_wallet.db")
    wallet = SpotSubWalletManager(db_path=db_file)

    state = wallet.get_wallet_state()
    assert state.initial_balance_usd == 10000.0
    assert state.usdt_available_balance == 10000.0
    assert state.allocated_margin_usd == 0.0

    # Reserve $500 margin for trade
    reserved = wallet.reserve_margin(500.0)
    assert reserved is True

    state_after_res = wallet.get_wallet_state()
    assert state_after_res.usdt_available_balance == 9500.0
    assert state_after_res.allocated_margin_usd == 500.0

    # Release margin with +$60 profit (+12% TP)
    wallet.release_margin(margin_usd=500.0, net_pnl_usd=60.0, is_win=True)
    state_after_win = wallet.get_wallet_state()
    assert state_after_win.usdt_available_balance == 10060.0
    assert state_after_win.allocated_margin_usd == 0.0
    assert state_after_win.realized_pnl_usd == 60.0
    assert state_after_win.winning_trades_count == 1
    assert state_after_win.total_trades_count == 1

    # Reset wallet
    wallet.reset_wallet(5000.0)
    state_reset = wallet.get_wallet_state()
    assert state_reset.initial_balance_usd == 5000.0
    assert state_reset.usdt_available_balance == 5000.0
    assert state_reset.realized_pnl_usd == 0.0

def test_spot_autonomous_bot_config_and_status(tmp_path):
    db_file = str(tmp_path / "test_spot_bot.db")
    wallet = SpotSubWalletManager(db_path=db_file)
    bot = SpotAutonomousBot(sub_wallet=wallet, db_path=db_file)

    # Verify default config
    cfg = bot.config
    assert cfg.allocation_per_trade_usd == 250.0
    assert cfg.max_active_positions == 5

    # Update config with custom capital
    new_cfg = SpotBotConfig(
        is_enabled=True,
        allocation_per_trade_usd=500.0,
        max_active_positions=3,
        min_opportunity_score=70.0,
        max_risk_score=45.0,
        take_profit_pct=15.0,
        stop_loss_pct=4.0
    )
    bot.save_config(new_cfg)
    assert bot.config.allocation_per_trade_usd == 500.0
    assert bot.config.max_active_positions == 3

    status = bot.get_status()
    assert status["config"]["allocation_per_trade_usd"] == 500.0
    assert status["wallet"]["total_equity_usd"] >= 5000.0

def test_spot_bot_self_learning_extraction(tmp_path):
    db_file = str(tmp_path / "test_spot_learning.db")
    wallet = SpotSubWalletManager(db_path=db_file)
    bot = SpotAutonomousBot(sub_wallet=wallet, db_path=db_file)

    sample_trade = {
        "trade_id": "TEST-TRD-01",
        "symbol": "PEPEUSDT",
        "category": "MEME",
        "exchange": "BINANCE",
        "entry_price": 0.000010,
        "quantity": 25000000.0,
        "position_size_usd": 250.0,
        "stop_loss_price": 0.0000095,
        "take_profit_price": 0.0000115,
        "opportunity_score": 82.0,
        "risk_score": 35.0,
        "status": "OPEN",
        "entry_ts": time.time()
    }

    # Simulate Take-Profit win
    bot._extract_and_apply_lesson(sample_trade, "TAKE_PROFIT", net_pnl_usd=30.0, pnl_pct=12.0)
    assert len(bot.learned_lessons) == 1
    assert bot.learned_lessons[0].outcome == "WIN_TP"
    assert "PEPEUSDT" in bot.learned_lessons[0].lesson_text

    # Simulate Stop-Loss trigger
    bot._extract_and_apply_lesson(sample_trade, "STOP_LOSS", net_pnl_usd=-12.5, pnl_pct=-5.0)
    assert len(bot.learned_lessons) == 2
    assert bot.learned_lessons[0].outcome == "LOSS_SL"
