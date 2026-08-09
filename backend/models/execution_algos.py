from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.session import Base

class ExecutionAlgorithmModel(Base):
    """Execution Algorithms Catalog Table."""
    __tablename__ = "execution_algorithms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    algo_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String, default="ACTIVE")

class ExecutionOrderModel(Base):
    """Execution Orders Table."""
    __tablename__ = "execution_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    algo: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)

class ExecutionSliceModel(Base):
    """Execution Slices Table."""
    __tablename__ = "execution_slices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slice_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    order_id: Mapped[str] = mapped_column(String, index=True, nullable=False)

class ExecutionFillModel(Base):
    """Execution Fills Table."""
    __tablename__ = "execution_fills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    fill_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class VenueExecutionStatModel(Base):
    """Venue Execution Stats Table."""
    __tablename__ = "venue_execution_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    venue: Mapped[str] = mapped_column(String, nullable=False)

class SlippagePredictionModel(Base):
    """Slippage Predictions Table."""
    __tablename__ = "slippage_predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    pred_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class TCAReportModel(Base):
    """TCA Reports Table."""
    __tablename__ = "tca_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    report_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class ExecutionReplayModel(Base):
    """Execution Replays Table."""
    __tablename__ = "execution_replays"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    replay_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class BenchmarkResultModel(Base):
    """Benchmark Results Table."""
    __tablename__ = "benchmark_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    benchmark_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class ExecutionQualityScoreModel(Base):
    """Execution Quality Scores Table."""
    __tablename__ = "execution_quality_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    score_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class VenueLatencySampleModel(Base):
    """Venue Latency Samples Table."""
    __tablename__ = "venue_latency_samples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    venue: Mapped[str] = mapped_column(String, nullable=False)

class LiquiditySnapshotModel(Base):
    """Liquidity Snapshots Table."""
    __tablename__ = "liquidity_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    snapshot_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
