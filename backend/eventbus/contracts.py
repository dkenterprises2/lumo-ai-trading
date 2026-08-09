import time
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class BaseEvent(BaseModel):
    event_id: str = Field(..., description="Unique event identifier")
    tenant_id: str = Field(default="ORG-101", description="Tenant isolation scope")
    event_type: str = Field(..., description="Event contract type name")
    timestamp: float = Field(default_factory=time.time)

class OrderCreatedEvent(BaseEvent):
    event_type: str = "OrderCreatedEvent"
    order_id: str
    symbol: str
    side: str
    quantity: float
    order_type: str

class OrderFilledEvent(BaseEvent):
    event_type: str = "OrderFilledEvent"
    order_id: str
    fill_price: float
    filled_quantity: float
    fee: float

class PositionOpenedEvent(BaseEvent):
    event_type: str = "PositionOpenedEvent"
    position_id: str
    symbol: str
    entry_price: float

class PositionClosedEvent(BaseEvent):
    event_type: str = "PositionClosedEvent"
    position_id: str
    pnl: float

class PortfolioUpdatedEvent(BaseEvent):
    event_type: str = "PortfolioUpdatedEvent"
    total_equity: float
    sharpe_ratio: float

class SignalGeneratedEvent(BaseEvent):
    event_type: str = "SignalGeneratedEvent"
    symbol: str
    action: str
    confidence: float

class RiskAlertEvent(BaseEvent):
    event_type: str = "RiskAlertEvent"
    alert_level: str
    message: str

class DriftDetectedEvent(BaseEvent):
    event_type: str = "DriftDetectedEvent"
    psi_score: float
    model_id: str

class RetrainingTriggeredEvent(BaseEvent):
    event_type: str = "RetrainingTriggeredEvent"
    job_id: str
    model_id: str

class InvoiceGeneratedEvent(BaseEvent):
    event_type: str = "InvoiceGeneratedEvent"
    invoice_id: str
    amount_usd: float

class TenantQuotaExceededEvent(BaseEvent):
    event_type: str = "TenantQuotaExceededEvent"
    quota_type: str
    usage_count: int

class SystemHealthChangedEvent(BaseEvent):
    event_type: str = "SystemHealthChangedEvent"
    service_name: str
    status: str
