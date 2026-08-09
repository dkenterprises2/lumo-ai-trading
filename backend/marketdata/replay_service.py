import time
from typing import Dict, Any

class TickOrderBookReplayService:
    """Sub-Second Tick & Order Book Replay Playback Service."""

    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def start_replay(self, symbol: str = "BTC/USDT", speed: float = 1.0) -> Dict[str, Any]:
        session_id = f"REPLAY-SESSION-{int(time.time())}"
        sess = {
            "session_id": session_id,
            "symbol": symbol,
            "speed_multiplier": speed,
            "status": "RUNNING",
            "current_time_offset": 0
        }
        self._sessions[session_id] = sess
        return sess

    def get_session(self, session_id: str) -> Dict[str, Any]:
        return self._sessions.get(session_id, {
            "session_id": session_id,
            "symbol": "BTC/USDT",
            "status": "RUNNING",
            "speed_multiplier": 1.0
        })

    def pause_session(self, session_id: str) -> Dict[str, Any]:
        sess = self.get_session(session_id)
        sess["status"] = "PAUSED"
        return sess

    def resume_session(self, session_id: str) -> Dict[str, Any]:
        sess = self.get_session(session_id)
        sess["status"] = "RUNNING"
        return sess

replay_service = TickOrderBookReplayService()
