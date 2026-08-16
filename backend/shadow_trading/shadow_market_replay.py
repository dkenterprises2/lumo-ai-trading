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
        self.default_playback_speed: int = 5

    def start_replay(
        self,
        symbol: str = "BTC/USDT",
        playback_speed: int = 5,
        duration_hours: float = 24.0
    ) -> ReplaySession:
        now = time.time()
        start_t = now - (duration_hours * 3600.0)
        chosen_speed = min(100, max(1, playback_speed or self.default_playback_speed))
        self.default_playback_speed = chosen_speed

        session = ReplaySession(
            symbol=symbol.upper(),
            start_time=start_t,
            end_time=now,
            playback_speed=chosen_speed,
            current_timestamp=start_t,
            status="RUNNING"
        )
        self.active_sessions[session.session_id] = session
        return session

    def stop_replay(self, session_id: str) -> Optional[ReplaySession]:
        session = self.active_sessions.get(session_id)
        if session:
            session.status = "COMPLETED"
            self.active_sessions.pop(session_id, None)
        return session

    def set_speed(self, speed: int, session_id: Optional[str] = None) -> int:
        clamped = min(100, max(1, speed))
        self.default_playback_speed = clamped
        if session_id and session_id in self.active_sessions:
            self.active_sessions[session_id].playback_speed = clamped
        else:
            for s in self.active_sessions.values():
                s.playback_speed = clamped
        return clamped
