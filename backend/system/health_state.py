from pydantic import BaseModel
from typing import Literal

class SystemHealthState(BaseModel):
    db_status: Literal["SYNCED", "PENDING", "FAILED"]
    websocket_status: Literal["CONNECTED", "CONNECTING", "RETRYING"]
    validation_status: Literal["VERIFIED", "PENDING", "FAILED"]
    trading_engine_status: Literal["ACTIVE", "DEGRADED", "STOPPED"]
    exchange_connectivity: bool
    portfolio_risk_ready: bool
    governance_ready: bool
    paper_trading_mode: bool = True
