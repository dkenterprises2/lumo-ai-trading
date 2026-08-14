import time
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Text
from backend.database.session import Base

class ExecutionOrderModel(Base):
    """SQLAlchemy model for OMS execution orders."""
    __tablename__ = "execution_orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(String(64), unique=True, index=True, nullable=False)
    client_order_id = Column(String(64), unique=True, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    symbol = Column(String(32), nullable=False)
    side = Column(String(16), nullable=False)
    order_type = Column(String(32), default="MARKET")
    quantity = Column(Float, nullable=False)
    filled_quantity = Column(Float, default=0.0)
    remaining_quantity = Column(Float, default=0.0)
    limit_price = Column(Float, nullable=True)
    average_fill_price = Column(Float, default=0.0)
    status = Column(String(32), default="DRAFT")
    exchange = Column(String(32), default="BINANCE")
    exchange_order_id = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=time.time)
    updated_at = Column(DateTime, default=time.time)
    metadata_json = Column(JSON, nullable=True)

class ExecutionFillModel(Base):
    """SQLAlchemy model for executed order fills."""
    __tablename__ = "execution_fills"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fill_id = Column(String(64), unique=True, index=True, nullable=False)
    order_id = Column(String(64), index=True, nullable=False)
    fill_price = Column(Float, nullable=False)
    fill_quantity = Column(Float, nullable=False)
    fee = Column(Float, default=0.0)
    liquidity_flag = Column(String(16), default="TAKER")
    exchange = Column(String(32), default="BINANCE")
    timestamp = Column(DateTime, default=time.time)

class ExecutionAuditModel(Base):
    """SQLAlchemy model for order state audit log."""
    __tablename__ = "execution_audits"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(String(64), index=True, nullable=False)
    event_type = Column(String(64), nullable=False)
    old_state = Column(String(32), nullable=False)
    new_state = Column(String(32), nullable=False)
    actor = Column(String(64), default="OMS_ENGINE")
    reason = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=time.time)
