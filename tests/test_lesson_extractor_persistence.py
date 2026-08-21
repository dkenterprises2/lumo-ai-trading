import os
import sys
import time
import json
import uuid
import pytest
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database.db_config import get_db_path, create_sqlite_connection
from backend.learning.lesson_extractor import LessonExtractorEngine, LearnedLesson


def test_lesson_extractor_db_path_initialization():
    engine = LessonExtractorEngine()
    assert hasattr(engine, "db_path")
    assert engine.db_path == get_db_path()
    assert os.path.exists(engine.db_path)


def test_lesson_extractor_save_and_retrieve_lesson():
    engine = LessonExtractorEngine()
    test_lesson_id = f"TEST-L-{uuid.uuid4().hex[:8].upper()}"

    lesson = LearnedLesson(
        lesson_id=test_lesson_id,
        title="Test Breakthrough Pullback Rejection",
        description="Test lesson verifying persistence and single-writer concurrency.",
        target_strategy="AI_HYBRID",
        market_regime="TRENDING_UP",
        trigger_conditions={"rsi_min": 45.0, "macd_cross": True},
        action_type="VETO_TRADE",
        confidence_score=0.88,
        evidence_count=5,
        sample_size=6,
        regimes_seen=["TRENDING_UP", "BULL_EXPANSION"],
        symbols_seen=["BTC/USDT", "ETH/USDT"],
        failure_count=1,
        quality_score=85.0,
        status="APPROVED",
        origin="REGRESSION_TEST",
        created_at=time.time(),
        last_validated_at=time.time()
    )

    # 1. Save lesson to DB
    engine._save_lesson_to_db(lesson)

    # 2. Verify row exists via direct SQLite read
    with create_sqlite_connection(engine.db_path, read_only=True) as conn:
        row = conn.execute(
            "SELECT * FROM learned_lessons WHERE lesson_id = ?",
            (test_lesson_id,)
        ).fetchone()

        assert row is not None
        assert row["lesson_id"] == test_lesson_id
        assert row["title"] == "Test Breakthrough Pullback Rejection"
        assert row["target_strategy"] == "AI_HYBRID"
        assert row["market_regime"] == "TRENDING_UP"
        assert row["status"] == "APPROVED"
        assert row["confidence_score"] == pytest.approx(0.88, 0.001)

    # 3. Verify engine reload / restart recovery
    engine.lessons.clear()
    engine._load_lessons_from_db()
    assert test_lesson_id in engine.lessons
    recovered = engine.lessons[test_lesson_id]
    assert recovered.title == "Test Breakthrough Pullback Rejection"
    assert recovered.evidence_count == 5

    # 4. Clean up test record only
    with create_sqlite_connection(engine.db_path) as conn:
        conn.execute("DELETE FROM learned_lessons WHERE lesson_id = ?", (test_lesson_id,))
        conn.commit()
    engine.lessons.pop(test_lesson_id, None)


def test_lesson_extraction_and_reinforcement_lifecycle():
    engine = LessonExtractorEngine()
    test_title = f"Dynamic Test Pattern {uuid.uuid4().hex[:6]}"

    # First extraction -> creates HYPOTHESIS
    l1 = engine.extract_or_update_lesson(
        title=test_title,
        description="Initial extraction description",
        regime="HIGH_VOLATILITY",
        trigger_conditions={"atr_ratio": 2.5},
        action_type="REDUCE_SIZE_50",
        confidence=0.75,
        symbol="SOL/USDT",
        origin="POST_MORTEM_RCA"
    )
    assert l1.lesson_id in engine.lessons
    assert l1.status == "HYPOTHESIS"
    assert l1.evidence_count == 1

    # Second extraction -> reinforces existing lesson
    l2 = engine.extract_or_update_lesson(
        title=test_title,
        description="Initial extraction description",
        regime="HIGH_VOLATILITY",
        trigger_conditions={"atr_ratio": 2.5},
        action_type="REDUCE_SIZE_50",
        confidence=0.80,
        symbol="ETH/USDT",
        origin="POST_MORTEM_RCA"
    )
    assert l2.lesson_id == l1.lesson_id
    assert l2.evidence_count == 2
    assert "ETH/USDT" in l2.symbols_seen

    # Clean up test lesson
    with create_sqlite_connection(engine.db_path) as conn:
        conn.execute("DELETE FROM learned_lessons WHERE lesson_id = ?", (l1.lesson_id,))
        conn.commit()
    engine.lessons.pop(l1.lesson_id, None)