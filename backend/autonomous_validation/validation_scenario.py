import time
import uuid
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

class ValidationState(str, Enum):
    DETECTED = "DETECTED"
    VALIDATING = "VALIDATING"
    RISK_CHECK = "RISK_CHECK"
    GOVERNANCE_CHECK = "GOVERNANCE_CHECK"
    APPROVED = "APPROVED"
    EXECUTING = "EXECUTING"
    PARTIAL_FILL = "PARTIAL_FILL"
    FILLED = "FILLED"
    POSITION_OPEN = "POSITION_OPEN"
    MONITORING = "MONITORING"
    EXIT_TRIGGERED = "EXIT_TRIGGERED"
    CLOSING = "CLOSING"
    CLOSED = "CLOSED"
    COMPLETED = "COMPLETED"

    # Rejection States
    REJECTED_UNPROFITABLE = "REJECTED_UNPROFITABLE"
    REJECTED_STALE_DATA = "REJECTED_STALE_DATA"
    REJECTED_RISK = "REJECTED_RISK"
    REJECTED_GOVERNANCE = "REJECTED_GOVERNANCE"
    REJECTED_KILL_SWITCH = "REJECTED_KILL_SWITCH"
    REJECTED_LIQUIDITY = "REJECTED_LIQUIDITY"
    REJECTED_DEGRADED = "REJECTED_DEGRADED"

@dataclass
class ReplayTickData:
    symbol: str = "BTC/USDT"
    buy_exchange: str = "BINANCE"
    sell_exchange: str = "BYBIT"
    buy_price: float = 100000.0
    sell_price: float = 100500.0
    buy_depth_usd: float = 100000.0
    sell_depth_usd: float = 100000.0
    data_age_ms: float = 15.0
    status: str = "FRESH"
    news_alert: Optional[str] = None
    exchange_health: str = "ONLINE"
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ValidationScenario:
    scenario_id: str
    code: str  # SCENARIO_A, SCENARIO_B, etc.
    title: str
    description: str
    category: str  # PROFITABLE, REJECTION, SAFETY, EXIT
    ticks: List[ReplayTickData]
    expected_terminal_state: str
    expected_should_execute: bool
    expected_should_exit: bool = False
    requires_kill_switch: bool = False
    requires_risk_breach: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["ticks"] = [t.to_dict() if hasattr(t, "to_dict") else t for t in self.ticks]
        return d

@dataclass
class ScenarioResult:
    scenario_id: str
    scenario_code: str
    title: str
    passed: bool
    execution_id: Optional[str]
    actual_terminal_state: str
    expected_terminal_state: str
    realized_shadow_pnl: float
    state_history: List[Dict[str, Any]]
    duration_ms: float
    notes: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
