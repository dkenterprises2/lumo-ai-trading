from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.session import Base

class ExchangeAccountModel(Base):
    """Connected Exchange Credentials & Status Table."""
    __tablename__ = "exchange_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    exchange_name: Mapped[str] = mapped_column(String, index=True, nullable=False)  # BINANCE_SPOT, BINANCE_FUTURES, BYBIT, OKX
    api_key_encrypted: Mapped[str] = mapped_column(String, nullable=False)
    secret_key_encrypted: Mapped[str] = mapped_column(String, nullable=False)
    is_testnet: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class ExchangeOrderModel(Base):
    """Exchange Order History Table."""
    __tablename__ = "exchange_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    client_order_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    exchange_order_id: Mapped[Optional[str]] = mapped_column(String, index=True)
    exchange_name: Mapped[str] = mapped_column(String, nullable=False)
    symbol: Mapped[str] = mapped_column(String, nullable=False)
    side: Mapped[str] = mapped_column(String, nullable=False)  # BUY, SELL
    order_type: Mapped[str] = mapped_column(String, nullable=False)  # MARKET, LIMIT, STOP, BRACKET
    status: Mapped[str] = mapped_column(String, nullable=False)  # OPEN, FILLED, CANCELLED, REJECTED
    amount_usd: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    filled_amount_usd: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "client_order_id": self.client_order_id,
            "exchange_order_id": self.exchange_order_id,
            "exchange_name": self.exchange_name,
            "symbol": self.symbol,
            "side": self.side,
            "order_type": self.order_type,
            "status": self.status,
            "amount_usd": self.amount_usd,
            "price": self.price,
            "filled_amount_usd": self.filled_amount_usd
        }
