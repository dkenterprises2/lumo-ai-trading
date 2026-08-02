import time
import pytest
from datetime import timedelta
from backend.core.config import settings
from backend.core.logger import (
    logger,
    log_trade,
    log_signal,
    log_ai_reasoning,
    log_execution_latency
)
from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    encrypt_api_key,
    decrypt_api_key
)

def test_config_settings():
    """Test enterprise settings instantiation and defaults."""
    assert settings.APP_NAME == "Lumo AI Trading Platform"
    assert settings.APP_VERSION == "2.5.0"
    assert "BTC/USDT" in settings.SUPPORTED_SYMBOLS
    assert "SOL/USDT" in settings.SUPPORTED_SYMBOLS
    assert settings.PAPER_TRADING_INITIAL_BALANCE == 10000.0
    assert settings.DEFAULT_RISK_PER_TRADE_PCT == 2.0
    assert len(settings.NEWS_RSS_FEEDS) >= 3

def test_logger_functions():
    """Test Loguru structured logger execution."""
    # Ensure helper log functions run without exceptions
    log_trade(action="BUY", symbol="BTC/USDT", price=65000.0, amount=0.1, pnl=0.0, reason="RSI Oversold")
    log_signal(symbol="ETH/USDT", action="STRONG_BUY", confidence=88.5, tech_score=80.0, sentiment_score=90.0)
    log_ai_reasoning(symbol="SOL/USDT", reasoning="Multi-timeframe EMA bullish crossover with news sentiment boost.")
    log_execution_latency(operation="Indicator Calculation", latency_ms=1.45)
    assert True

def test_password_hashing():
    """Test PBKDF2 HMAC SHA-256 password hashing and verification."""
    password = "SuperSecretSecurePassword123!"
    hashed = hash_password(password)

    assert hashed != password
    assert len(hashed) > 20

    # Valid password verify
    assert verify_password(password, hashed) is True

    # Invalid password verify
    assert verify_password("WrongPassword123!", hashed) is False
    assert verify_password("", hashed) is False
    assert verify_password(password, "") is False
    assert verify_password("pass", "invalid_base64_hash_###") is False

    # Empty password exception check
    with pytest.raises(ValueError):
        hash_password("")


def test_jwt_token_lifecycle():
    """Test JWT token creation, signature verification, and expiration."""
    user_data = {"sub": "trader_101", "email": "quant@lumo.ai", "role": "admin"}
    token = create_access_token(data=user_data, expires_delta=timedelta(minutes=5))

    assert isinstance(token, str)
    assert len(token.split('.')) == 3

    # Verify valid token
    decoded = verify_token(token)
    assert decoded is not None
    assert decoded["sub"] == "trader_101"
    assert decoded["role"] == "admin"

    # Test expired token
    expired_token = create_access_token(data=user_data, expires_delta=timedelta(seconds=-10))
    assert verify_token(expired_token) is None

    # Test tampered token
    tampered_token = token[:-5] + "XXXXX"
    assert verify_token(tampered_token) is None

def test_api_key_encryption():
    """Test AES-256 Fernet API key encryption and decryption."""
    api_key = "binance_live_api_key_998877665544332211"
    encrypted = encrypt_api_key(api_key)

    assert encrypted != api_key
    assert len(encrypted) > 10

    # Decrypt and compare
    decrypted = decrypt_api_key(encrypted)
    assert decrypted == api_key

    # Test empty input handling
    assert encrypt_api_key("") == ""
    assert decrypt_api_key("") == ""

    # Test tampered cipher text
    with pytest.raises(ValueError):
        decrypt_api_key("InvalidTamperedCipherData")

if __name__ == "__main__":
    pytest.main(["-v", __file__])
