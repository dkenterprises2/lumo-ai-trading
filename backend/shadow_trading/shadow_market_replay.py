import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

@dataclass
class ReplaySession:
    session_id: str = field(default_factory=lambda: f"REPLAY-{uuid.uuid4().hex[:8].upper()}")
    symbol: str = "BTC/USDT"
    start_time: float = field(default_factory=lambda: time.time() - 86400.0)
    end_time: float = field(default_factory=time.time)
    playback_speed: int = 1  # 1x, 5x, 10x, 50x
    current_timestamp: float = field(default_factory=time.time)
    status: str = "IDLE"  # IDLE, RUNNING, PAUSED, COMPLETED

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ShadowMarketReplay:
    """Historical Candle, Orderbook & Trade Tape Replay Engine."""

    def __init__(self):
        self.active_sessions: Dict[str, ReplaySession] = {}

    def start_replay(
        self,
        symbol: str = "BTC/USDT",
        playback_speed: int = 5,
        duration_hours: float = 24.0
    ) -> ReplaySession:
        now = time.time()
        start_t = now - (duration_hours * 3600.0)

        session = ReplaySession(
            symbol=symbol.upper(),
            start_time=start_t,
            end_time=now,
            playback_speed=min(50, max(1, playback_speed)),
            current_timestamp=start_t,
            status="RUNNING"
        )
        self.active_sessions[session.session_id] = session
        return session

    def stop_replay(self, session_id: str) -> Optional[ReplaySession]:
        session = self.active_sessions.get(session_id)
        if session:
            session.status = "COMPLETED"
        return session
