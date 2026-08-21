import time
import uuid
import sqlite3
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from loguru import logger
from backend.database.db_config import get_db_path, create_sqlite_connection
from .lesson_extractor import lesson_extractor

@dataclass
class HumanFeedbackRecord:
    feedback_id: str = field(default_factory=lambda: f"FB-{uuid.uuid4().hex[:6].upper()}")
    experience_id: str = ""
    user_id: str = "1"
    rating: str = "CORRECT"  # CORRECT, INCORRECT, PARTIALLY_CORRECT, IRRELEVANT
    user_notes: str = ""
    suggested_action: Optional[str] = None
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class HumanFeedbackManager:
    """Human-in-the-Loop Feedback & Annotation Manager.
    
    Treats human reviews as candidate hypotheses requiring empirical validation
    before rule promotion, preventing emotional or single-event rule tampering.
    """

    DB_PATH = get_db_path()
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HumanFeedbackManager, cls).__new__(cls)
            cls._instance._init_db()
        return cls._instance

    def _get_conn(self) -> sqlite3.Connection:
        return create_sqlite_connection(self.DB_PATH, timeout=60.0)

    def _init_db(self):
        try:
            with self._get_conn() as conn:
                conn.execute("""
                CREATE TABLE IF NOT EXISTS human_feedback (
                    feedback_id TEXT PRIMARY KEY,
                    experience_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    rating TEXT NOT NULL,
                    user_notes TEXT NOT NULL,
                    suggested_action TEXT,
                    created_at REAL NOT NULL
                );
                """)
                conn.commit()
        except Exception as e:
            logger.error(f"[HumanFeedbackManager] DB init error: {e}")

    def record_feedback(
        self,
        experience_id: str,
        user_id: str,
        rating: str,
        user_notes: str,
        suggested_action: Optional[str] = None
    ) -> HumanFeedbackRecord:
        fb = HumanFeedbackRecord(
            experience_id=experience_id,
            user_id=str(user_id),
            rating=rating.upper(),
            user_notes=user_notes,
            suggested_action=suggested_action
        )

        try:
            with self._get_conn() as conn:
                conn.execute("""
                INSERT INTO human_feedback (feedback_id, experience_id, user_id, rating, user_notes, suggested_action, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (fb.feedback_id, fb.experience_id, fb.user_id, fb.rating, fb.user_notes, fb.suggested_action, fb.created_at))
                conn.commit()
        except Exception as e:
            logger.error(f"[HumanFeedbackManager] Save feedback error: {e}")

        # If user flagged a critical flaw, extract a candidate HYPOTHESIS lesson
        if rating.upper() in ["INCORRECT", "PARTIALLY_CORRECT"] and len(user_notes) > 5:
            lesson_extractor.extract_or_update_lesson(
                title=f"User Feedback: {user_notes[:40]}...",
                description=user_notes,
                regime="ANY",
                trigger_conditions={"origin": "USER_FEEDBACK", "notes": user_notes},
                action_type="VETO_TRADE" if "avoid" in user_notes.lower() or "late" in user_notes.lower() else "REDUCE_SIZE_50",
                confidence=0.60,
                origin="HUMAN_FEEDBACK"
            )

        return fb

    def get_feedback_for_experience(self, experience_id: str) -> List[Dict[str, Any]]:
        results = []
        try:
            with self._get_conn() as conn:
                rows = conn.execute("SELECT * FROM human_feedback WHERE experience_id = ?", (experience_id,)).fetchall()
                for r in rows:
                    results.append(dict(r))
        except Exception as e:
            logger.error(f"[HumanFeedbackManager] Fetch error: {e}")
        return results

# Global Singleton
human_feedback_manager = HumanFeedbackManager()
