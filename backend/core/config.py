import os
import secrets
from typing import List, Dict, Any, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """Production Enterprise Configuration for Lumo AI Trading Platform."""

    # Application Settings
    APP_NAME: str = "Lumo AI Trading Platform"
    APP_VERSION: str = "2.5.0"
    ENVIRONMENT: str = Field(default="development", description="development, staging, or production")
    DEBUG: bool = Field(default=True)
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)

    # Security & Cryptography
    SECRET_KEY: str = Field(default="lumo-trading-jwt-secret-key-production-2026-stable-v1")
    ENCRYPTION_KEY: str = Field(
        default_factory=lambda: "e1e8Z3Q5X0R5W1R3X0R5W1R3X0R5W1R3X0R5W1R3X0Q="
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 Hours

    # Database Configuration
    DATABASE_URL: str = Field(default=f"sqlite+aiosqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '../../lumo_trading.db'))}")
    ASYNC_DATABASE_URL: str = Field(default=f"sqlite+aiosqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '../../lumo_trading.db'))}")
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20


    # Redis Cache & PubSub
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    REDIS_CACHE_TTL_SECONDS: int = 300

    # Supported Crypto Assets (Multi-Symbol Scanner - 50 Top Crypto Pairs)
    SUPPORTED_SYMBOLS: List[str] = [
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT", "DOGE/USDT", "AVAX/USDT", "DOT/USDT", "LINK/USDT",
        "MATIC/USDT", "ATOM/USDT", "NEAR/USDT", "APT/USDT", "SUI/USDT", "OP/USDT", "ARB/USDT", "LTC/USDT", "ETC/USDT", "XLM/USDT",
        "FIL/USDT", "INJ/USDT", "TIA/USDT", "UNI/USDT", "ICP/USDT", "FET/USDT", "RNDR/USDT", "PEPE/USDT", "SHIB/USDT", "FLOKI/USDT",
        "AAVE/USDT", "MKR/USDT", "SNX/USDT", "CRV/USDT", "LDO/USDT", "GRT/USDT", "ALGO/USDT", "FTM/USDT", "SAND/USDT", "MANA/USDT",
        "THETA/USDT", "AXS/USDT", "EGLD/USDT", "EOS/USDT", "FLOW/USDT", "KAVA/USDT", "MINA/USDT", "QNT/USDT", "RUNE/USDT", "WOO/USDT"
    ]

    # Timeframes Supported
    SUPPORTED_TIMEFRAMES: List[str] = [
        "1m", "3m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"
    ]

    # Trading Strategies Supported
    SUPPORTED_STRATEGIES: List[str] = [
        "AI Hybrid",
        "Trend Following",
        "Breakout",
        "Scalping",
        "Grid",
        "DCA",
        "Swing"
    ]

    # Trading Engine Defaults
    LIVE_TRADING_ENABLED: bool = False             # Strict safety invariant: live trading disabled
    PAPER_TRADING_INITIAL_BALANCE: float = 10000.0  # Virtual USDT
    DEFAULT_RISK_PER_TRADE_PCT: float = 2.0         # 2% portfolio risk per position
    MAX_DAILY_LOSS_PCT: float = 5.0                # 5% max portfolio daily loss
    MAX_DRAWDOWN_PCT: float = 15.0                 # 15% circuit breaker
    MAX_OPEN_POSITIONS: int = 50

    DEFAULT_STOP_LOSS_PCT: float = 2.5             # 2.5% stop loss
    DEFAULT_TAKE_PROFIT_PCT: float = 5.0            # 5.0% take profit
    DEFAULT_LEVERAGE: int = 1                       # Default 1x (Spot / Cross)

    # External APIs & News Feed Endpoints
    FEAR_GREED_API_URL: str = "https://api.alternative.me/fng/?limit=1"
    CRYPTO_PANIC_API_URL: str = "https://cryptopanic.com/api/v1/posts/"
    NEWS_RSS_FEEDS: List[Dict[str, str]] = [
        {"name": "CoinTelegraph", "url": "https://cointelegraph.com/rss"},
        {"name": "CoinDesk", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/"},
        {"name": "Bitcoin Magazine", "url": "https://bitcoinmagazine.com/feed"},
        {"name": "CryptoSlate", "url": "https://cryptoslate.com/feed/"}
    ]

    # Optional AI Keys
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
