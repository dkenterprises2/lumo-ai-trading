import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_api_market_summary():
    response = client.get("/api/market-summary?symbol=BTC/USDT&timeframe=1h")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "BTC/USDT"
    assert "current_price" in data
    assert "chart_data" in data

def test_api_news_sentiment():
    response = client.get("/api/news-sentiment")
    assert response.status_code == 200
    data = response.json()
    assert "fear_greed" in data
    assert "sentiment_summary" in data

def test_api_ai_signal():
    response = client.get("/api/ai-signal/BTC/USDT?strategy=AI Hybrid")
    assert response.status_code == 200
    data = response.json()
    assert "action" in data
    assert "confidence_score" in data

def test_api_portfolio():
    response = client.get("/api/portfolio")
    assert response.status_code == 200
    data = response.json()
    assert "usdt_balance" in data
    assert "total_portfolio_value" in data

def test_api_execute_order():
    payload = {
        "symbol": "BTC/USDT",
        "side": "LONG",
        "order_type": "MARKET",
        "allocation_usd": 1000.0,
        "leverage": 1,
        "stop_loss_price": 63000.0,
        "take_profit_price": 68000.0
    }
    response = client.post("/api/trade/order", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_api_position_action():
    payload = {
        "symbol": "BTC/USDT",
        "action": "CLOSE"
    }
    response = client.post("/api/trade/position-action", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_api_toggle_bot():
    response = client.post("/api/bot/toggle?enable=true")
    assert response.status_code == 200
    data = response.json()
    assert data["auto_bot_enabled"] is True
