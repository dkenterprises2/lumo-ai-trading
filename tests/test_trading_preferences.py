import pytest
import asyncio
import time
from fastapi.testclient import TestClient
from main import app
from backend.database.session import init_db
from backend.repositories.trading_preferences_repo import trading_preferences_repo
from institutional_risk import InstitutionalRiskManager, InstitutionalRiskConfig

client = TestClient(app)

@pytest.mark.asyncio
async def test_default_trading_preferences_creation():
    await init_db()
    prefs = await trading_preferences_repo.get_by_user_id(user_id=9901)
    assert prefs is not None
    assert prefs.user_id == 9901
    assert prefs.max_concurrent_trades == 3
    assert prefs.max_capital_per_trade_pct == 10.0
    assert prefs.daily_loss_limit_pct == 5.0
    assert prefs.symbol_cooldown_minutes == 15
    assert isinstance(prefs.allowed_symbols, list)
    assert "BTC/USDT" in prefs.allowed_symbols


@pytest.mark.asyncio
async def test_plan_tier_limits_enforcement():
    await init_db()

    # FREE tier cap is 2
    updated, err = await trading_preferences_repo.update_by_user_id(
        user_id=9902,
        updates={"max_concurrent_trades": 5},
        user_plan="FREE"
    )
    assert updated is None
    assert err is not None
    assert "FREE" in err or "2" in err

    # Valid FREE tier setting (2)
    updated, err = await trading_preferences_repo.update_by_user_id(
        user_id=9902,
        updates={"max_concurrent_trades": 2},
        user_plan="FREE"
    )
    assert err is None
    assert updated.max_concurrent_trades == 2

    # PRO tier cap is 10 (setting to 8 is valid)
    updated, err = await trading_preferences_repo.update_by_user_id(
        user_id=9903,
        updates={"max_concurrent_trades": 8},
        user_plan="PRO"
    )
    assert err is None
    assert updated.max_concurrent_trades == 8

    # PRO tier exceeding cap (setting to 15 is rejected)
    updated, err = await trading_preferences_repo.update_by_user_id(
        user_id=9903,
        updates={"max_concurrent_trades": 15},
        user_plan="PRO"
    )
    assert updated is None
    assert "PRO" in err or "10" in err


def test_preferences_api_endpoints():
    response = client.get("/api/preferences/trading")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "success"
    assert "data" in json_data
    assert "max_concurrent_trades" in json_data["data"]
    assert "plan_max_concurrent_trades" in json_data["data"]

    # Test PUT update
    update_res = client.put(
        "/api/preferences/trading",
        json={
            "max_concurrent_trades": 2,
            "max_capital_per_trade_pct": 15.0,
            "symbol_cooldown_minutes": 10,
            "allowed_symbols": ["BTC/USDT", "ETH/USDT"]
        }
    )
    assert update_res.status_code == 200
    res_data = update_res.json()
    assert res_data["status"] == "success"
    assert res_data["data"]["max_capital_per_trade_pct"] == 15.0
    assert res_data["data"]["allowed_symbols"] == ["BTC/USDT", "ETH/USDT"]


def test_institutional_risk_user_preferences():
    # Mock user trader
    class MockUserTrader:
        def __init__(self):
            self.usdt_balance = 10000.0
            self.initial_balance = 10000.0
            self.positions = {}
            self.peak_equity = 10000.0
            self.symbol_exit_timestamps = {}

        def get_portfolio_summary(self, prices):
            return {"total_portfolio_value": 10000.0, "daily_pnl_usd": 0.0}

    mock_trader = MockUserTrader()

    # Config with allowed_symbols=["BTC/USDT"], max_capital_per_trade_pct=10.0%, max_concurrent_trades=2, symbol_cooldown_minutes=15
    config = InstitutionalRiskConfig(
        max_concurrent_trades=2,
        max_capital_per_trade_pct=10.0,
        symbol_cooldown_minutes=15,
        allowed_symbols=["BTC/USDT"]
    )
    risk_mgr = InstitutionalRiskManager(config)

    # Test 1: Symbol not allowed rejection
    res1 = risk_mgr.evaluate_order_risk(mock_trader, "ETH/USDT", "BUY", 3500.0, 500.0)
    assert res1["passed"] is False
    assert res1["rule"] == "SYMBOL_NOT_ALLOWED"

    # Test 2: Max capital per trade exceeded rejection ($1500 > 10% of $10,000 = $1000)
    res2 = risk_mgr.evaluate_order_risk(mock_trader, "BTC/USDT", "BUY", 65000.0, 1500.0)
    assert res2["passed"] is False
    assert res2["rule"] == "MAX_CAPITAL_PER_TRADE"

    # Test 3: Valid order passing all risk rules ($800 <= $1000 cap)
    res3 = risk_mgr.evaluate_order_risk(mock_trader, "BTC/USDT", "BUY", 65000.0, 800.0)
    assert res3["passed"] is True

    # Test 4: Symbol cooldown active rejection
    mock_trader.symbol_exit_timestamps["BTC/USDT"] = time.time() - (5 * 60) # exited 5 mins ago (cooldown 15 mins)
    res4 = risk_mgr.evaluate_order_risk(mock_trader, "BTC/USDT", "BUY", 65000.0, 800.0)
    assert res4["passed"] is False
    assert res4["rule"] == "SYMBOL_COOLDOWN_ACTIVE"
