import time
import logging
from typing import Dict, List, Any

logger = logging.getLogger("stuck_position_detector")

class StuckPositionDetector:
    """Detects positions remaining open beyond configured maximum holding time."""

    def __init__(self, max_holding_seconds: float = 600.0):
        self.max_holding_seconds = max_holding_seconds

    def audit_and_unwind_stuck_positions(self, execution_manager: Any) -> List[Dict[str, Any]]:
        now = time.time()
        unwind_reports = []

        for pos_id, pos in list(execution_manager.positions.items()):
            status = getattr(pos, 'status', pos.get('status') if isinstance(pos, dict) else 'UNKNOWN')
            entry_ts = getattr(pos, 'entry_timestamp', pos.get('entry_timestamp', now) if isinstance(pos, dict) else now)
            holding_sec = now - entry_ts

            if status in ["OPEN", "MONITORING"] and holding_sec > self.max_holding_seconds:
                logger.warning(f"[STUCK_POSITION_DETECTOR] Position {pos_id} held for {holding_sec:.1f}s (> {self.max_holding_seconds}s limit)")

                # Execute shadow exit
                if hasattr(execution_manager, 'exit_engine'):
                    pos_dict = pos.to_dict() if hasattr(pos, 'to_dict') else pos
                    exit_info = execution_manager.exit_engine.execute_shadow_exit(pos_dict, reason="MAX_HOLDING_TIME_EXCEEDED")
                    
                    if hasattr(pos, 'status'):
                        pos.status = "CLOSED"
                        pos.exit_timestamp = now
                        pos.exit_reason = "MAX_HOLDING_TIME_EXCEEDED"
                    else:
                        pos['status'] = "CLOSED"
                        pos['exit_timestamp'] = now
                        pos['exit_reason'] = "MAX_HOLDING_TIME_EXCEEDED"

                    rep = {
                        "position_id": pos_id,
                        "holding_seconds": round(holding_sec, 1),
                        "action": "AUTOMATED_UNWIND_EXECUTED",
                        "exit_info": exit_info
                    }
                    unwind_reports.append(rep)

        return unwind_reports

stuck_position_detector = StuckPositionDetector()
