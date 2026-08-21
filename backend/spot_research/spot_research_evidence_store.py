import uuid
"""
Forensic Evidence Store for Lumo Spot Research Subsystem.
Maintains an immutable, auditable SQLite ledger of every coin discovery,
classification, AI research analysis, and paper-trade validation event.
Supports filtering, detail inspection, CSV export, and JSON export.
"""

import os
import time
import json
import csv
import io
import queue
import threading
import sqlite3
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from loguru import logger
from backend.database.db_config import get_db_path, create_sqlite_connection

class SpotResearchForensicEvent(BaseModel):
    event_id: str
    timestamp: float = Field(default_factory=time.time)
    symbol: str
    exchange: str
    category: str
    price_usd: Optional[float] = None
    volume_24h_usd: Optional[float] = None
    liquidity_usd: Optional[float] = None
    spread_bps: Optional[float] = None
    opportunity_score: float
    risk_score: float
    recommendation: str
    data_sources: List[str] = Field(default_factory=list)
    raw_dossier_json: str

class SpotResearchEvidenceStore:
    """Thread-safe, micro-batched forensic evidence persistence store for Spot Research."""

    def __init__(self):
        self.db_path = get_db_path()
        self._write_queue = queue.Queue(maxsize=10000)
        self._stop_event = threading.Event()
        self._init_db_schema()

        self._worker_thread = threading.Thread(
            target=self._persistence_worker,
            daemon=True,
            name="SpotResearchEvidenceWorker"
        )
        self._worker_thread.start()

    def _init_db_schema(self):
        conn = create_sqlite_connection(self.db_path)
        try:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS spot_research_evidence_events (
                event_id TEXT PRIMARY KEY,
                timestamp REAL NOT NULL,
                symbol TEXT NOT NULL,
                exchange TEXT NOT NULL,
                category TEXT NOT NULL,
                price_usd REAL,
                volume_24h_usd REAL,
                liquidity_usd REAL,
                spread_bps REAL,
                opportunity_score REAL NOT NULL,
                risk_score REAL NOT NULL,
                recommendation TEXT NOT NULL,
                data_sources TEXT NOT NULL,
                raw_dossier_json TEXT NOT NULL,
                created_at REAL DEFAULT (strftime('%s', 'now'))
            );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_spot_ev_sym ON spot_research_evidence_events(symbol);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_spot_ev_cat ON spot_research_evidence_events(category);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_spot_ev_ts ON spot_research_evidence_events(timestamp);")
            conn.commit()
        finally:
            conn.close()


    def record_evidence_event(self, event_type: str, symbol: str, actor: str, data: Dict[str, Any]):
        """Helper to record structured evidence event."""
        now = time.time()
        ev = SpotResearchForensicEvent(
            event_id=f"EV-{uuid.uuid4().hex[:8].upper()}",
            timestamp=now,
            symbol=symbol,
            exchange=data.get("exchange", "BINANCE"),
            category=data.get("category", "SPOT_RESEARCH"),
            price_usd=data.get("entry_price") or data.get("price_usd"),
            volume_24h_usd=data.get("volume_24h_usd"),
            liquidity_usd=data.get("liquidity_usd"),
            spread_bps=data.get("spread_bps"),
            opportunity_score=data.get("opp_score", 70.0),
            risk_score=data.get("risk_score", 40.0),
            recommendation=data.get("recommendation", "PAPER_TEST"),
            data_sources=["SPOT_AUTONOMOUS_BOT"],
            raw_dossier_json=json.dumps(data)
        )
        self.record_event(ev)

    def record_event(self, event: SpotResearchForensicEvent):
        try:
            self._write_queue.put_nowait(event)
        except queue.Full:
            logger.warning("[SPOT_EVIDENCE] Queue full, dropping event")

    def _persistence_worker(self):
        while not self._stop_event.is_set():
            batch: List[SpotResearchForensicEvent] = []
            try:
                item = self._write_queue.get(timeout=0.05)
                batch.append(item)
                while len(batch) < 100:
                    try:
                        batch.append(self._write_queue.get_nowait())
                    except queue.Empty:
                        break
            except queue.Empty:
                continue

            if batch:
                self._insert_batch(batch)

    def _insert_batch(self, batch: List[SpotResearchForensicEvent]):
        conn = create_sqlite_connection(self.db_path, timeout=10.0)
        try:
            records = [
                (
                    e.event_id, e.timestamp, e.symbol, e.exchange, e.category,
                    e.price_usd, e.volume_24h_usd, e.liquidity_usd, e.spread_bps,
                    e.opportunity_score, e.risk_score, e.recommendation,
                    json.dumps(e.data_sources), e.raw_dossier_json
                )
                for e in batch
            ]
            conn.executemany("""
            INSERT OR REPLACE INTO spot_research_evidence_events (
                event_id, timestamp, symbol, exchange, category,
                price_usd, volume_24h_usd, liquidity_usd, spread_bps,
                opportunity_score, risk_score, recommendation,
                data_sources, raw_dossier_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, records)
            conn.commit()
        except Exception as ex:
            logger.error(f"[SPOT_EVIDENCE_PERSIST_ERR] {ex}")
        finally:
            conn.close()

    def query_events(self, limit: int = 50, category: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = create_sqlite_connection(self.db_path)
        try:
            conn.row_factory = sqlite3.Row
            if category:
                rows = conn.execute(
                    "SELECT * FROM spot_research_evidence_events WHERE category = ? ORDER BY timestamp DESC LIMIT ?",
                    (category.upper(), limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM spot_research_evidence_events ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def export_csv(self, limit: int = 1000) -> str:
        events = self.query_events(limit=limit)
        output = io.StringIO()
        fieldnames = [
            "event_id", "timestamp", "symbol", "exchange", "category",
            "price_usd", "volume_24h_usd", "liquidity_usd", "spread_bps",
            "opportunity_score", "risk_score", "recommendation", "data_sources"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for ev in events:
            writer.writerow(ev)
        return output.getvalue()

    def export_json(self, limit: int = 1000) -> List[Dict[str, Any]]:
        return self.query_events(limit=limit)

spot_research_evidence_store = SpotResearchEvidenceStore()
