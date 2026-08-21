from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
from .lesson_extractor import lesson_extractor, LearnedLesson

@dataclass
class LessonApplicationResult:
    lesson_applied: bool = False
    matching_lesson_id: Optional[str] = None
    matching_lesson_title: Optional[str] = None
    action: str = "PROCEED"  # PROCEED, VETO_TRADE, REDUCE_SIZE_50, DEMAND_HIGHER_EDGE
    sizing_multiplier: float = 1.0
    reason: str = "No conflicting learned rules triggered."

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class NextTradeLessonApplicationEngine:
    """Deterministic Pre-Trade Learned Rule Application Engine.
    
    Intercepts candidate trading setups before risk gate to enforce empirically
    validated learned rules and prevent repeating historical mistakes.
    """

    def evaluate_candidate_against_lessons(
        self,
        symbol: str,
        direction: str,
        market_regime: str,
        signal_features: Dict[str, Any]
    ) -> LessonApplicationResult:
        active_lessons = lesson_extractor.get_active_approved_lessons()
        rsi = float(signal_features.get("rsi", 50.0))
        vol_ratio = float(signal_features.get("volume_ma_ratio", 1.5))
        adx = float(signal_features.get("adx", 20.0))

        for lesson in active_lessons:
            conds = lesson.trigger_conditions
            
            # Check regime match
            if lesson.market_regime != "ANY" and lesson.market_regime != market_regime:
                continue

            # Check direction match
            if "direction" in conds and conds["direction"] != direction.upper():
                continue

            # Check RSI threshold trigger
            if "rsi_below" in conds and rsi >= conds["rsi_below"]:
                continue
            if "rsi_above" in conds and rsi <= conds["rsi_above"]:
                continue

            # Check Volume MA threshold trigger
            if "volume_ma_ratio_below" in conds and vol_ratio >= conds["volume_ma_ratio_below"]:
                continue

            # Check ADX threshold trigger
            if "adx_above" in conds and adx <= conds["adx_above"]:
                continue

            # Lesson triggers!
            if lesson.action_type == "VETO_TRADE":
                return LessonApplicationResult(
                    lesson_applied=True,
                    matching_lesson_id=lesson.lesson_id,
                    matching_lesson_title=lesson.title,
                    action="VETO_TRADE",
                    sizing_multiplier=0.0,
                    reason=f"Vetoed by Approved Lesson {lesson.lesson_id} ('{lesson.title}'): Confidence {lesson.confidence_score*100:.0f}% with {lesson.evidence_count} historical evidence trades."
                )
            elif lesson.action_type == "REDUCE_SIZE_50":
                return LessonApplicationResult(
                    lesson_applied=True,
                    matching_lesson_id=lesson.lesson_id,
                    matching_lesson_title=lesson.title,
                    action="REDUCE_SIZE_50",
                    sizing_multiplier=0.5,
                    reason=f"Downsized 50% by Lesson {lesson.lesson_id} ('{lesson.title}'): Sub-optimal volume/regime profile."
                )
            elif lesson.action_type in ("BOOST_ALPHA", "PROCEED"):
                return LessonApplicationResult(
                    lesson_applied=True,
                    matching_lesson_id=lesson.lesson_id,
                    matching_lesson_title=lesson.title,
                    action="BOOST_ALPHA",
                    sizing_multiplier=1.2,
                    reason=f"🚀 Boosted by Approved Alpha Technique {lesson.lesson_id} ('{lesson.title}'): High historical win-rate ({lesson.confidence_score*100:.0f}%)."
                )

        return LessonApplicationResult(
            lesson_applied=False,
            action="PROCEED",
            sizing_multiplier=1.0,
            reason="All active quantitative learning rules validated setup cleanly."
        )

# Global Singleton
lesson_applier = NextTradeLessonApplicationEngine()
