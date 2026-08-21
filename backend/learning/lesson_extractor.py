import time
import uuid
import json
import sqlite3
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from loguru import logger
from backend.database.db_config import get_db_path, create_sqlite_connection

@dataclass
class LearnedLesson:
    """Authoritative Learned Quantitative Rule / Lesson Object."""
    lesson_id: str = field(default_factory=lambda: f"L-{uuid.uuid4().hex[:6].upper()}")
    title: str = ""
    description: str = ""
    target_strategy: str = "ALL"
    market_regime: str = "ANY"
    trigger_conditions: Dict[str, Any] = field(default_factory=dict)
    action_type: str = "VETO_TRADE"  # VETO_TRADE, REDUCE_SIZE_50, TIGHTEN_SL, DEMAND_HIGHER_EDGE
    confidence_score: float = 0.50   # [0.0, 1.0]
    evidence_count: int = 1          # Number of trades backing this lesson
    sample_size: int = 1
    regimes_seen: List[str] = field(default_factory=list)
    symbols_seen: List[str] = field(default_factory=list)
    failure_count: int = 0
    quality_score: float = 50.0      # [0.0, 100.0]
    status: str = "HYPOTHESIS"       # HYPOTHESIS, VALIDATED, APPROVED, RETIRED
    origin: str = "POST_MORTEM_RCA"  # POST_MORTEM_RCA, HUMAN_FEEDBACK, ARBITRAGE_FAILURE
    created_at: float = field(default_factory=time.time)
    last_validated_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class LessonExtractorEngine:
    """Quantitative Lesson Extraction, Quality Scoring & Promotion Lifecycle Engine with Persistent SQLite Storage."""

    _instance = None

    def __new__(cls, db_path: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super(LessonExtractorEngine, cls).__new__(cls)
            cls._instance.db_path = db_path or get_db_path()
            cls._instance.DB_PATH = cls._instance.db_path
            cls._instance.lessons: Dict[str, LearnedLesson] = {}
            cls._instance._init_db()
        elif db_path and db_path != cls._instance.db_path:
            cls._instance.db_path = db_path
            cls._instance.DB_PATH = db_path
        return cls._instance

    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = db_path
            self.DB_PATH = db_path
        elif not hasattr(self, "db_path"):
            self.db_path = get_db_path()
            self.DB_PATH = self.db_path

    def _get_conn(self) -> sqlite3.Connection:
        target_path = getattr(self, "db_path", None) or get_db_path()
        return create_sqlite_connection(target_path, timeout=60.0)

    def _init_db(self):
        conn = None
        try:
            conn = self._get_conn()
            conn.execute("""
            CREATE TABLE IF NOT EXISTS learned_lessons (
                lesson_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                target_strategy TEXT NOT NULL,
                market_regime TEXT NOT NULL,
                trigger_conditions TEXT NOT NULL,
                action_type TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                evidence_count INTEGER NOT NULL,
                sample_size INTEGER NOT NULL,
                regimes_seen TEXT NOT NULL,
                symbols_seen TEXT NOT NULL,
                failure_count INTEGER NOT NULL,
                quality_score REAL NOT NULL,
                status TEXT NOT NULL,
                origin TEXT NOT NULL,
                created_at REAL NOT NULL,
                last_validated_at REAL NOT NULL
            );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_lesson_status ON learned_lessons(status);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_lesson_regime ON learned_lessons(market_regime);")
            conn.commit()
            conn.close()
            conn = None

            self._load_lessons_from_db()
            if not self.lessons:
                self._seed_canonical_lessons()
        except Exception as e:
            logger.error(f"[LessonExtractorEngine] DB Init error: {e}")
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def _load_lessons_from_db(self):
        conn = None
        try:
            conn = self._get_conn()
            cursor = conn.execute("SELECT * FROM learned_lessons;")
            rows = cursor.fetchall()
            for r in rows:
                l = LearnedLesson(
                    lesson_id=r["lesson_id"],
                    title=r["title"],
                    description=r["description"],
                    target_strategy=r["target_strategy"],
                    market_regime=r["market_regime"],
                    trigger_conditions=json.loads(r["trigger_conditions"]),
                    action_type=r["action_type"],
                    confidence_score=r["confidence_score"],
                    evidence_count=r["evidence_count"],
                    sample_size=r["sample_size"],
                    regimes_seen=json.loads(r["regimes_seen"]),
                    symbols_seen=json.loads(r["symbols_seen"]),
                    failure_count=r["failure_count"],
                    quality_score=r["quality_score"],
                    status=r["status"],
                    origin=r["origin"],
                    created_at=r["created_at"],
                    last_validated_at=r["last_validated_at"]
                )
                self.lessons[l.lesson_id] = l
        except Exception as e:
            logger.error(f"[LessonExtractorEngine] Error loading lessons: {e}")
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def _save_lesson_to_db(self, lesson: LearnedLesson):
        from backend.database.db_config import execute_write_with_retry

        def _write_op(conn: sqlite3.Connection):
            conn.execute("""
            INSERT INTO learned_lessons (
                lesson_id, title, description, target_strategy, market_regime,
                trigger_conditions, action_type, confidence_score, evidence_count,
                sample_size, regimes_seen, symbols_seen, failure_count,
                quality_score, status, origin, created_at, last_validated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(lesson_id) DO UPDATE SET
                title=excluded.title,
                description=excluded.description,
                target_strategy=excluded.target_strategy,
                market_regime=excluded.market_regime,
                trigger_conditions=excluded.trigger_conditions,
                action_type=excluded.action_type,
                confidence_score=excluded.confidence_score,
                evidence_count=excluded.evidence_count,
                sample_size=excluded.sample_size,
                regimes_seen=excluded.regimes_seen,
                symbols_seen=excluded.symbols_seen,
                failure_count=excluded.failure_count,
                quality_score=excluded.quality_score,
                status=excluded.status,
                origin=excluded.origin,
                last_validated_at=excluded.last_validated_at;
            """, (
                lesson.lesson_id, lesson.title, lesson.description, lesson.target_strategy,
                lesson.market_regime, json.dumps(lesson.trigger_conditions), lesson.action_type,
                lesson.confidence_score, lesson.evidence_count, lesson.sample_size,
                json.dumps(lesson.regimes_seen), json.dumps(lesson.symbols_seen), lesson.failure_count,
                lesson.quality_score, lesson.status, lesson.origin, lesson.created_at, lesson.last_validated_at
            ))
            return True

        target_path = getattr(self, "db_path", None) or get_db_path()
        try:
            execute_write_with_retry(
                _write_op,
                writer_name="LessonExtractorEngine",
                table_or_query="learned_lessons",
                max_retries=10,
                db_path=target_path
            )
        except Exception as e:
            logger.error(f"[LessonExtractorEngine] Error saving lesson: {e}", exc_info=True)
            raise

    def _seed_canonical_lessons(self):
        """Seed initial foundational hypothesis lessons."""
        l1 = LearnedLesson(
            lesson_id="L-101",
            title="Late Short Momentum Trap in Recovery Regimes",
            description="Shorting oversold assets (RSI < 28) during recovery/reversal regimes exhibits negative expectancy.",
            market_regime="RECOVERY_REVERSAL",
            trigger_conditions={"direction": "SHORT", "rsi_below": 28.0, "regime": "RECOVERY_REVERSAL"},
            action_type="VETO_TRADE",
            confidence_score=0.84,
            evidence_count=12,
            sample_size=15,
            regimes_seen=["RECOVERY_REVERSAL", "RANGING_CHOP"],
            symbols_seen=["BTC/USDT", "ETH/USDT", "SOL/USDT"],
            quality_score=86.5,
            status="APPROVED"
        )
        l2 = LearnedLesson(
            lesson_id="L-102",
            title="Unconfirmed Breakout Low-Volume Penalty",
            description="Breakout entries with volume < 1.2x 20-period moving average suffer high failure rates.",
            market_regime="BREAKOUT_EXPANSION",
            trigger_conditions={"direction": "LONG", "volume_ma_ratio_below": 1.2, "regime": "BREAKOUT_EXPANSION"},
            action_type="REDUCE_SIZE_50",
            confidence_score=0.78,
            evidence_count=8,
            sample_size=10,
            regimes_seen=["BREAKOUT_EXPANSION"],
            symbols_seen=["BTC/USDT", "AVAX/USDT"],
            quality_score=78.0,
            status="APPROVED"
        )
        self.lessons[l1.lesson_id] = l1
        self.lessons[l2.lesson_id] = l2
        self._save_lesson_to_db(l1)
        self._save_lesson_to_db(l2)

    def calculate_quality_score(self, lesson: LearnedLesson) -> float:
        """Compute holistic quality score [0.0 - 100.0]."""
        ev_score = min(35.0, lesson.evidence_count * 5.0)
        conf_score = lesson.confidence_score * 35.0
        regime_div = min(15.0, len(lesson.regimes_seen) * 5.0)
        symbol_div = min(15.0, len(lesson.symbols_seen) * 3.0)
        penalty = lesson.failure_count * 10.0
        
        score = max(0.0, min(100.0, ev_score + conf_score + regime_div + symbol_div - penalty))
        return round(score, 1)

    def extract_or_update_lesson(
        self,
        title: str,
        description: str,
        regime: str,
        trigger_conditions: Dict[str, Any],
        action_type: str = "VETO_TRADE",
        confidence: float = 0.70,
        symbol: str = "BTC/USDT",
        origin: str = "POST_MORTEM_RCA"
    ) -> LearnedLesson:
        """Extract a new lesson or reinforce an existing pattern."""
        matched = None
        for l in self.lessons.values():
            if l.market_regime == regime and l.action_type == action_type and l.title == title:
                matched = l
                break

        if matched:
            matched.evidence_count += 1
            matched.sample_size += 1
            matched.confidence_score = min(0.99, round(matched.confidence_score * 0.95 + confidence * 0.05, 3))
            if symbol not in matched.symbols_seen:
                matched.symbols_seen.append(symbol)
            if regime not in matched.regimes_seen:
                matched.regimes_seen.append(regime)
            matched.quality_score = self.calculate_quality_score(matched)
            matched.last_validated_at = time.time()
            
            # Promotion to APPROVED
            if matched.status in ["HYPOTHESIS", "VALIDATED"] and matched.evidence_count >= 5 and matched.confidence_score >= 0.75 and matched.quality_score >= 70.0:
                matched.status = "APPROVED"
                logger.info(f"[LESSON_PROMOTED] Lesson {matched.lesson_id} ('{matched.title}') promoted to APPROVED rule.")
            self._save_lesson_to_db(matched)
            return matched
        else:
            new_id = f"L-{uuid.uuid4().hex[:6].upper()}"
            lesson = LearnedLesson(
                lesson_id=new_id,
                title=title,
                description=description,
                market_regime=regime,
                trigger_conditions=trigger_conditions,
                action_type=action_type,
                confidence_score=confidence,
                evidence_count=1,
                sample_size=1,
                regimes_seen=[regime] if regime != "ANY" else [],
                symbols_seen=[symbol],
                quality_score=self.calculate_quality_score(LearnedLesson(confidence_score=confidence, evidence_count=1)),
                status="HYPOTHESIS",
                origin=origin
            )
            self.lessons[new_id] = lesson
            self._save_lesson_to_db(lesson)
            return lesson

    def get_active_approved_lessons(self) -> List[LearnedLesson]:
        """Return all active APPROVED lessons that can influence the decision layer."""
        return [l for l in self.lessons.values() if l.status == "APPROVED"]

    def set_lesson_status(self, lesson_id: str, new_status: str) -> bool:
        """Explicit governance state change: ACTIVATE, DEACTIVATE, ROLLBACK, RETIRE."""
        if lesson_id in self.lessons:
            self.lessons[lesson_id].status = new_status.upper()
            self.lessons[lesson_id].last_validated_at = time.time()
            self._save_lesson_to_db(self.lessons[lesson_id])
            logger.info(f"[LESSON_STATE_CHANGE] Lesson {lesson_id} state updated to {new_status.upper()}.")
            return True
        return False

# Global Singleton
lesson_extractor = LessonExtractorEngine()
