import time
import logging
from typing import Dict, List, Any

logger = logging.getLogger("stuck_job_detector")

class StuckJobDetector:
    """Detects stalled executions in intermediate lifecycle states."""

    def __init__(self, max_stuck_seconds: float = 30.0):
        self.max_stuck_seconds = max_stuck_seconds

    def audit_and_recover_stuck_jobs(self, execution_manager: Any) -> List[Dict[str, Any]]:
        now = time.time()
        stuck_reports = []

        for exec_id, rec in list(execution_manager.executions.items()):
            status = getattr(rec, 'status', rec.get('status') if isinstance(rec, dict) else 'UNKNOWN')
            created_at = getattr(rec, 'created_at', rec.get('created_at', now) if isinstance(rec, dict) else now)
            age_sec = now - created_at

            if status in ["STARTING", "EXECUTING", "PARTIAL_FILL", "CLOSING"] and age_sec > self.max_stuck_seconds:
                logger.warning(f"[STUCK_JOB_DETECTOR] Job {exec_id} stuck in {status} for {age_sec:.1f}s")
                
                new_status = "RECOVERY_REQUIRED"
                if isinstance(rec, dict):
                    rec['status'] = new_status
                else:
                    rec.status = new_status

                rep = {
                    "execution_id": exec_id,
                    "previous_status": status,
                    "new_status": new_status,
                    "stuck_duration_sec": round(age_sec, 1),
                    "action": "TRANSITIONED_TO_RECOVERY_REQUIRED"
                }
                stuck_reports.append(rep)

        return stuck_reports

stuck_job_detector = StuckJobDetector()
