import time
import uuid
import math
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

@dataclass
class ReplayTick:
    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    buy_depth_usd: float
    sell_depth_usd: float
    timestamp: float
    data_age_ms: float = 15.0
    status: str = "FRESH"
    news_alert: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class AutonomousReplaySession:
    session_id: str = field(default_factory=lambda: f"REPLAY-{uuid.uuid4().hex[:8].upper()}")
    symbol: str = "BTC/USDT"
    scenario: str = "FLASH_SPREAD_DISCREPANCY"
    playback_speed: int = 5
    start_time: float = field(default_factory=time.time)
    current_tick_index: int = 0
    total_ticks: int = 0
    status: str = "IDLE"  # IDLE, RUNNING, PAUSED, COMPLETED
    opportunities_detected: int = 0
    executions_triggered: int = 0
    positions_opened: int = 0
    positions_closed: int = 0
    net_pnl_usd: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class AutonomousMarketReplay:
    """Historical Market Replay Engine for Autonomous Shadow Trading Validation."""

    SCENARIOS = [
        "FLASH_SPREAD_DISCREPANCY",
        "ORDERBOOK_IMBALANCE_REPLAY",
        "STALE_QUOTE_STRESS",
        "NEWS_SHOCK_REPLAY"
    ]

    def __init__(self):
        self.active_session: Optional[AutonomousReplaySession] = None
        self.tick_buffer: List[ReplayTick] = []

    def generate_scenario_ticks(self, scenario: str, symbol: str = "BTC/USDT", count: int = 30) -> List[ReplayTick]:
        """Generate deterministic, real micro-structure tick sequences for historical replay scenarios."""
        now = time.time()
        ticks: List[ReplayTick] = []

        base_price = 100000.0

        for i in range(count):
            tick_time = now - ((count - i) * 2.0)

            if scenario == "FLASH_SPREAD_DISCREPANCY":
                # Gross spread varies between 0.40% and 0.85% (Executable after 0.15% fee/slippage friction)
                spread_pct = 0.0040 + (0.0045 * (1.0 + math.sin(i / 3.0)) / 2.0)
                buy_p = base_price + (i * 5.0)
                sell_p = buy_p * (1.0 + spread_pct)
                depth = 150000.0
                age_ms = 15.0
                st = "FRESH"
                alert = None

            elif scenario == "ORDERBOOK_IMBALANCE_REPLAY":
                # High spread but shallow depth requiring ICEBERG / TWAP algorithm selection
                spread_pct = 0.0050
                buy_p = base_price
                sell_p = buy_p * (1.0 + spread_pct)
                depth = 8000.0 if i < 15 else 45000.0  # Shallow depth initially
                age_ms = 20.0
                st = "FRESH"
                alert = None

            elif scenario == "STALE_QUOTE_STRESS":
                # Quote age spikes above 2000ms threshold
                buy_p = base_price
                sell_p = base_price * 1.0060
                depth = 100000.0
                age_ms = 2500.0 if (5 <= i <= 15) else 25.0
                st = "DATA_STALE" if age_ms > 2000.0 else "FRESH"
                alert = None

            elif scenario == "NEWS_SHOCK_REPLAY":
                # Normal spread followed by sudden exchange security alert
                buy_p = base_price
                sell_p = base_price * 1.0050
                depth = 100000.0
                age_ms = 18.0
                st = "FRESH"
                alert = "EXCHANGE_HACK" if i >= 10 else None

            else:
                buy_p = base_price
                sell_p = base_price * 1.0005  # Inexecutable spread (< fees)
                depth = 100000.0
                age_ms = 12.0
                st = "FRESH"
                alert = None

            ticks.append(ReplayTick(
                symbol=symbol,
                buy_exchange="BINANCE",
                sell_exchange="BYBIT",
                buy_price=round(buy_p, 2),
                sell_price=round(sell_p, 2),
                buy_depth_usd=depth,
                sell_depth_usd=depth,
                timestamp=tick_time,
                data_age_ms=age_ms,
                status=st,
                news_alert=alert
            ))

        return ticks

    def start_replay_session(
        self,
        symbol: str = "BTC/USDT",
        scenario: str = "FLASH_SPREAD_DISCREPANCY",
        playback_speed: int = 5
    ) -> AutonomousReplaySession:
        if scenario not in self.SCENARIOS:
            scenario = "FLASH_SPREAD_DISCREPANCY"

        ticks = self.generate_scenario_ticks(scenario, symbol=symbol, count=30)
        self.tick_buffer = ticks

        session = AutonomousReplaySession(
            symbol=symbol.upper(),
            scenario=scenario,
            playback_speed=min(50, max(1, playback_speed)),
            start_time=time.time(),
            current_tick_index=0,
            total_ticks=len(ticks),
            status="RUNNING"
        )
        self.active_session = session
        return session

    def stop_replay_session(self) -> Optional[AutonomousReplaySession]:
        if self.active_session:
            self.active_session.status = "COMPLETED"
        return self.active_session

    def get_next_tick(self) -> Optional[ReplayTick]:
        if not self.active_session or self.active_session.status != "RUNNING":
            return None

        idx = self.active_session.current_tick_index
        if idx >= len(self.tick_buffer):
            self.active_session.status = "COMPLETED"
            return None

        tick = self.tick_buffer[idx]
        self.active_session.current_tick_index += 1
        return tick

    def get_status(self) -> Dict[str, Any]:
        if not self.active_session:
            return {"status": "IDLE", "active_session": None}
        return {"status": self.active_session.status, "session": self.active_session.to_dict()}
