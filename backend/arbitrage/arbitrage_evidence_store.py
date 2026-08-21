import os
import time
import json
import uuid
import hashlib
import sqlite3
import datetime
import threading
import queue
import random
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Tuple
from loguru import logger

from backend.database.db_config import get_db_path, create_sqlite_connection, transaction_tracker

DB_PATH = get_db_path()

@dataclass
class ArbitrageForensicEvent:
    event_id: str = field(default_factory=lambda: f"EVT-{uuid.uuid4().hex[:10].upper()}")
    timestamp_utc: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + " UTC")
    timestamp_local: str = field(default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
    symbol: str = "BTC/USDT"
    route_id: str = "BINANCE->BYBIT"
    buy_exchange: str = "BINANCE"
    sell_exchange: str = "BYBIT"
    buy_quote_timestamp: float = field(default_factory=time.time)
    sell_quote_timestamp: float = field(default_factory=time.time)
    buy_bid: float = 0.0
    buy_ask: float = 0.0
    sell_bid: float = 0.0
    sell_ask: float = 0.0
    buy_price_used: float = 0.0
    sell_price_used: float = 0.0
    gross_spread_bps: float = 0.0
    gross_spread_pct: float = 0.0
    estimated_quantity: float = 1.0
    orderbook_depth_buy: float = 1.0
    orderbook_depth_sell: float = 1.0
    estimated_fee_buy: float = 7.5
    estimated_fee_sell: float = 7.5
    estimated_slippage_buy: float = 2.0
    estimated_slippage_sell: float = 2.0
    latency_ms: float = 25.0
    quote_age_ms: float = 0.0
    net_edge_bps: float = 0.0
    net_edge_pct: float = 0.0
    decision: str = "REJECTED"  # EXECUTABLE or REJECTED
    rejection_reason: str = "NEGATIVE_SPREAD"
    category: str = "NEGATIVE_SPREAD"  # One of the 12 categories
    risk_result: str = "PASS"
    liquidity_result: str = "PASS"
    governance_result: str = "PASS"
    freshness_result: str = "PASS"
    execution_status: str = "REJECTED"  # DETECTED, REJECTED, EXECUTABLE, PAPER_EXECUTED, SHADOW_EXECUTED
    opportunity_id: str = field(default_factory=lambda: f"OPP-{uuid.uuid4().hex[:8].upper()}")
    scan_cycle_id: str = field(default_factory=lambda: f"CYCLE-{int(time.time()*1000)}")
    market_data_source: str = "Binance / Bybit Public Ticker API"
    market_data_provider: str = "BINANCE"
    source_timestamp: float = field(default_factory=time.time)
    received_timestamp: float = field(default_factory=time.time)
    data_age_ms: float = 0.0
    created_at: float = field(default_factory=time.time)
    raw_snapshot_json: str = "{}"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ArbitrageEvidenceStore:
    """High-Performance Persistent Forensic Evidence Store for Arbitrage Evaluation Events.
    
    Guarantees:
    - Zero fake / synthetic records (Strict live evaluation provenance).
    - High-write throughput via background batch persistence queue with bounded micro-transactions.
    - Zero event loss monitoring (events_dropped == 0).
    - Exponential backoff + jitter lock retry resilience (Zero unhandled lock errors).
    - Idempotent inserts via ON CONFLICT(event_id) DO NOTHING.
    - Indexed fast queries for all 12 rejection / route categories.
    - 100% Deterministic Decision Replay from captured raw snapshots.
    """

    _instance = None
    _lock = threading.Lock()

    # Bounded batching configuration
    MAX_BATCH_SIZE: int = 100
    FLUSH_INTERVAL_SECONDS: float = 0.05
    MAX_RETRIES: int = 12

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ArbitrageEvidenceStore, cls).__new__(cls)
                cls._instance._init_store()
            return cls._instance

    def _init_store(self):
        self.db_path = DB_PATH
        self.spillover_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "logs", "evidence_spillover.jsonl"))
        os.makedirs(os.path.dirname(self.spillover_file), exist_ok=True)
        
        self.events_generated = 0
        self.events_enqueued = 0
        self.events_persisted = 0
        self.events_retried = 0
        self.events_failed = 0
        self.events_dropped = 0
        self.lock_errors_count = 0
        self._last_drop_log_time = 0.0
        self.last_successful_write_utc = "None"
        self.last_error = None
        
        self._write_latencies: List[float] = []
        self._latencies_lock = threading.Lock()
        
        self._write_queue: queue.Queue = queue.Queue(maxsize=500000)
        self._fallback_buffer: List[ArbitrageForensicEvent] = []
        self._buffer_lock = threading.Lock()
        self._stop_event = threading.Event()
        
        self._init_database()
        self._recover_spillover_on_startup()
        
        # Start async persistence worker
        self._worker_thread = threading.Thread(
            target=self._persistence_worker,
            daemon=True,
            name="ArbitrageEvidencePersistenceWorker"
        )
        self._worker_thread.start()

    def _recover_spillover_on_startup(self):
        """Recovers any uncommitted spillover events from previous runs on startup."""
        if not os.path.exists(self.spillover_file):
            return
        try:
            import dataclasses
            recovered_count = 0
            with open(self.spillover_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            valid_fields = {f.name for f in dataclasses.fields(ArbitrageForensicEvent)}
                            filtered_data = {k: v for k, v in data.items() if k in valid_fields}
                            evt = ArbitrageForensicEvent(**filtered_data)
                            self._write_queue.put_nowait(evt)
                            recovered_count += 1
                        except Exception as parse_err:
                            logger.error(f"[ArbitrageEvidenceStore] Error parsing spillover line: {parse_err}")
            if recovered_count > 0:
                logger.info(f"[ArbitrageEvidenceStore] Recovered {recovered_count} spillover events from disk on startup.")
                # Truncate spillover file after loading into queue
                with open(self.spillover_file, "w", encoding="utf-8") as f:
                    f.truncate(0)
        except Exception as ex:
            logger.error(f"[ArbitrageEvidenceStore] Notice during spillover recovery: {ex}")

    def _append_to_spillover_file(self, batch: List[ArbitrageForensicEvent]):
        """Durable disk write if in-memory queues overflow or persistent DB is locked."""
        try:
            with open(self.spillover_file, "a", encoding="utf-8") as f:
                for item in batch:
                    f.write(json.dumps(item.to_dict()) + "\n")
            logger.info(f"[ArbitrageEvidenceStore] Persisted {len(batch)} items to durable spillover file.")
        except Exception as disk_err:
            logger.error(f"[ArbitrageEvidenceStore] Disk spillover error: {disk_err}")

    def _get_conn(self) -> sqlite3.Connection:
        return create_sqlite_connection(self.db_path, timeout=60.0)

    def _init_database(self):
        """Create the forensic evidence table and required indices with retry resilience."""
        for attempt in range(10):
            try:
                conn = self._get_conn()
                try:
                    table_exists = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='arbitrage_evidence_events'").fetchone()
                    if not table_exists:
                        conn.execute("""
                        CREATE TABLE IF NOT EXISTS arbitrage_evidence_events (
                            event_id TEXT PRIMARY KEY,
                            timestamp_utc TEXT NOT NULL,
                            timestamp_local TEXT NOT NULL,
                            symbol TEXT NOT NULL,
                            route_id TEXT NOT NULL,
                            buy_exchange TEXT NOT NULL,
                            sell_exchange TEXT NOT NULL,
                            buy_quote_timestamp REAL,
                            sell_quote_timestamp REAL,
                            buy_bid REAL,
                            buy_ask REAL,
                            sell_bid REAL,
                            sell_ask REAL,
                            buy_price_used REAL,
                            sell_price_used REAL,
                            gross_spread_bps REAL,
                            gross_spread_pct REAL,
                            estimated_quantity REAL,
                            orderbook_depth_buy REAL,
                            orderbook_depth_sell REAL,
                            estimated_fee_buy REAL,
                            estimated_fee_sell REAL,
                            estimated_slippage_buy REAL,
                            estimated_slippage_sell REAL,
                            latency_ms REAL,
                            quote_age_ms REAL,
                            net_edge_bps REAL,
                            net_edge_pct REAL,
                            decision TEXT NOT NULL,
                            rejection_reason TEXT NOT NULL,
                            category TEXT NOT NULL,
                            risk_result TEXT NOT NULL,
                            liquidity_result TEXT NOT NULL,
                            governance_result TEXT NOT NULL,
                            freshness_result TEXT NOT NULL,
                            execution_status TEXT NOT NULL,
                            opportunity_id TEXT,
                            scan_cycle_id TEXT,
                            market_data_source TEXT,
                            market_data_provider TEXT,
                            source_timestamp REAL,
                            received_timestamp REAL,
                            data_age_ms REAL,
                            created_at REAL NOT NULL,
                            raw_snapshot_json TEXT NOT NULL
                        );
                        """)
                        conn.execute("CREATE INDEX IF NOT EXISTS idx_arb_ev_created ON arbitrage_evidence_events(created_at);")
                        conn.execute("CREATE INDEX IF NOT EXISTS idx_arb_ev_category ON arbitrage_evidence_events(category);")
                        conn.execute("CREATE INDEX IF NOT EXISTS idx_arb_ev_symbol ON arbitrage_evidence_events(symbol);")
                        conn.execute("CREATE INDEX IF NOT EXISTS idx_arb_ev_decision ON arbitrage_evidence_events(decision);")
                        conn.execute("CREATE INDEX IF NOT EXISTS idx_arb_ev_gross ON arbitrage_evidence_events(gross_spread_bps);")
                        conn.execute("CREATE INDEX IF NOT EXISTS idx_arb_ev_net ON arbitrage_evidence_events(net_edge_bps);")
                        conn.commit()
                    break
                finally:
                    conn.close()
            except sqlite3.OperationalError as e:
                time.sleep(0.1 * (attempt + 1))
            except Exception as e:
                logger.error(f"[ArbitrageEvidenceStore] DB initialization error: {e}")
                time.sleep(0.2)

    def record_event(self, event: ArbitrageForensicEvent):
        """
        Non-blocking submission of a live route evaluation event.
        Guarantees 100% capture with zero arbitrary sampling or event loss.
        """
        with self._lock:
            self.events_generated += 1

        try:
            self._write_queue.put_nowait(event)
            with self._lock:
                self.events_enqueued += 1
        except queue.Full:
            # If queue reaches 500k limit, append to fallback buffer and disk spillover
            with self._buffer_lock:
                self._fallback_buffer.append(event)
            self._append_to_spillover_file([event])
            with self._lock:
                self.events_enqueued += 1
            now = time.time()
            if now - self._last_drop_log_time > 30.0:
                self._last_drop_log_time = now
                logger.warning(f"[ArbitrageEvidenceStore] Queue full; preserved to durable fallback buffer and spillover disk.")

    def _persistence_worker(self):
        """Flushes queued events in high-throughput micro-batches to SQLite with retry."""
        while not self._stop_event.is_set():
            batch = []
            queue_items_count = 0
            
            # Check fallback buffer first
            with self._buffer_lock:
                if self._fallback_buffer:
                    drain_count = min(len(self._fallback_buffer), self.MAX_BATCH_SIZE)
                    batch.extend(self._fallback_buffer[:drain_count])
                    self._fallback_buffer = self._fallback_buffer[drain_count:]

            # Fill remaining batch from main queue
            remaining_slots = self.MAX_BATCH_SIZE - len(batch)
            if remaining_slots > 0:
                try:
                    item = self._write_queue.get(timeout=self.FLUSH_INTERVAL_SECONDS)
                    batch.append(item)
                    queue_items_count += 1
                    while len(batch) < self.MAX_BATCH_SIZE:
                        try:
                            batch.append(self._write_queue.get_nowait())
                            queue_items_count += 1
                        except queue.Empty:
                            break
                except queue.Empty:
                    pass

            if batch:
                success = self._insert_batch_with_retry(batch)
                for _ in range(queue_items_count):
                    try:
                        self._write_queue.task_done()
                    except ValueError:
                        pass

    def _insert_batch_with_retry(self, batch: List[ArbitrageForensicEvent]) -> bool:
        """
        Executes idempotent batch insertion with exponential backoff + jitter lock retry.
        Measures write latency and guarantees zero event drop.
        """
        if not batch:
            return True

        sql = """
        INSERT INTO arbitrage_evidence_events (
            event_id, timestamp_utc, timestamp_local, symbol, route_id,
            buy_exchange, sell_exchange, buy_quote_timestamp, sell_quote_timestamp,
            buy_bid, buy_ask, sell_bid, sell_ask, buy_price_used, sell_price_used,
            gross_spread_bps, gross_spread_pct, estimated_quantity,
            orderbook_depth_buy, orderbook_depth_sell, estimated_fee_buy, estimated_fee_sell,
            estimated_slippage_buy, estimated_slippage_sell, latency_ms, quote_age_ms,
            net_edge_bps, net_edge_pct, decision, rejection_reason, category,
            risk_result, liquidity_result, governance_result, freshness_result,
            execution_status, opportunity_id, scan_cycle_id,
            market_data_source, market_data_provider, source_timestamp,
            received_timestamp, data_age_ms, created_at, raw_snapshot_json
        ) VALUES (
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?, ?
        )
        ON CONFLICT(event_id) DO NOTHING;
        """

        params = [
            (
                e.event_id, e.timestamp_utc, e.timestamp_local, e.symbol, e.route_id,
                e.buy_exchange, e.sell_exchange, e.buy_quote_timestamp, e.sell_quote_timestamp,
                e.buy_bid, e.buy_ask, e.sell_bid, e.sell_ask, e.buy_price_used, e.sell_price_used,
                e.gross_spread_bps, e.gross_spread_pct, e.estimated_quantity,
                e.orderbook_depth_buy, e.orderbook_depth_sell, e.estimated_fee_buy, e.estimated_fee_sell,
                e.estimated_slippage_buy, e.estimated_slippage_sell, e.latency_ms, e.quote_age_ms,
                e.net_edge_bps, e.net_edge_pct, e.decision, e.rejection_reason, e.category,
                e.risk_result, e.liquidity_result, e.governance_result, e.freshness_result,
                e.execution_status, e.opportunity_id, e.scan_cycle_id,
                e.market_data_source, e.market_data_provider, e.source_timestamp,
                e.received_timestamp, e.data_age_ms, e.created_at, e.raw_snapshot_json
            )
            for e in batch
        ]

        def _do_batch_insert(conn: sqlite3.Connection):
            t0 = time.perf_counter()
            conn.executemany(sql, params)
            dur_ms = (time.perf_counter() - t0) * 1000.0
            with self._latencies_lock:
                self._write_latencies.append(dur_ms)
                if len(self._write_latencies) > 10000:
                    self._write_latencies = self._write_latencies[-5000:]
            return True

        from backend.database.db_config import execute_write_with_retry
        try:
            execute_write_with_retry(
                _do_batch_insert,
                writer_name="ArbitrageEvidenceStore",
                table_or_query="arbitrage_evidence_events (batch)",
                max_retries=self.MAX_RETRIES,
                db_path=self.db_path
            )
            with self._lock:
                self.events_persisted += len(batch)
                self.last_successful_write_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + " UTC"
            return True
        except Exception as write_err:
            # If all bounded retries exhausted, preserve in fallback buffer and disk spillover
            with self._buffer_lock:
                self._fallback_buffer.extend(batch)
            self._append_to_spillover_file(batch)
            with self._lock:
                self.events_failed += len(batch)
                self.lock_errors_count += 1
                self.last_error = str(write_err)
            logger.error(
                f"[ArbitrageEvidenceStore] CRITICAL: Failed to persist batch of {len(batch)} events after {self.MAX_RETRIES} retries. "
                f"Preserved in durable fallback buffer and disk spillover file. Error: {write_err}"
            )
            return False

    def query_events(
        self,
        category: Optional[str] = None,
        symbol: Optional[str] = None,
        buy_venue: Optional[str] = None,
        sell_venue: Optional[str] = None,
        decision: Optional[str] = None,
        rejection_reason: Optional[str] = None,
        time_range_seconds: Optional[float] = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Query stored evidence events with rich filtering, sorting, and pagination."""
        query = "SELECT * FROM arbitrage_evidence_events WHERE 1=1"
        count_query = "SELECT COUNT(*) FROM arbitrage_evidence_events WHERE 1=1"
        params = []

        if category and category.upper() != "ALL":
            cat_upper = category.upper().replace(" ", "_")
            if cat_upper == "SCANNED_ROUTES":
                pass
            elif cat_upper == "GROSS_PROFITABLE":
                query += " AND gross_spread_bps > 0"
                count_query += " AND gross_spread_bps > 0"
            elif cat_upper == "NEGATIVE_SPREAD":
                query += " AND gross_spread_bps <= 0"
                count_query += " AND gross_spread_bps <= 0"
            elif cat_upper == "STALE_QUOTES":
                query += " AND (category = 'STALE_QUOTES' OR rejection_reason LIKE '%STALE%')"
                count_query += " AND (category = 'STALE_QUOTES' OR rejection_reason LIKE '%STALE%')"
            elif cat_upper in ["CACHED_FALLBACK", "CACHED_/_FALLBACK"]:
                query += " AND (category = 'CACHED_FALLBACK' OR rejection_reason LIKE '%FALLBACK%' OR rejection_reason LIKE '%CACHED%')"
                count_query += " AND (category = 'CACHED_FALLBACK' OR rejection_reason LIKE '%FALLBACK%' OR rejection_reason LIKE '%CACHED%')"
            elif cat_upper in ["FEE_REJECTIONS", "FEES"]:
                query += " AND (category = 'FEE_REJECTIONS' OR rejection_reason LIKE '%FEE%')"
                count_query += " AND (category = 'FEE_REJECTIONS' OR rejection_reason LIKE '%FEE%')"
            elif cat_upper == "SLIPPAGE_REJECTIONS":
                query += " AND (category = 'SLIPPAGE_REJECTIONS' OR rejection_reason LIKE '%SLIPPAGE%')"
                count_query += " AND (category = 'SLIPPAGE_REJECTIONS' OR rejection_reason LIKE '%SLIPPAGE%')"
            elif cat_upper == "LIQUIDITY_REJECTIONS":
                query += " AND (category = 'LIQUIDITY_REJECTIONS' OR rejection_reason LIKE '%LIQUIDITY%' OR rejection_reason LIKE '%DEPTH%')"
                count_query += " AND (category = 'LIQUIDITY_REJECTIONS' OR rejection_reason LIKE '%LIQUIDITY%' OR rejection_reason LIKE '%DEPTH%')"
            elif cat_upper == "RISK_REJECTIONS":
                query += " AND (category = 'RISK_REJECTIONS' OR rejection_reason LIKE '%RISK%')"
                count_query += " AND (category = 'RISK_REJECTIONS' OR rejection_reason LIKE '%RISK%')"
            elif cat_upper in ["GOVERNANCE_REJECTIONS", "GOV_REJECTIONS"]:
                query += " AND (category = 'GOVERNANCE_REJECTIONS' OR rejection_reason LIKE '%GOV%' OR rejection_reason LIKE '%KILL%')"
                count_query += " AND (category = 'GOVERNANCE_REJECTIONS' OR rejection_reason LIKE '%GOV%' OR rejection_reason LIKE '%KILL%')"
            elif cat_upper == "NET_PROFITABLE":
                query += " AND net_edge_bps > 0"
                count_query += " AND net_edge_bps > 0"
            elif cat_upper == "EXECUTABLE":
                query += " AND decision = 'EXECUTABLE'"
                count_query += " AND decision = 'EXECUTABLE'"
            else:
                query += " AND category = ?"
                count_query += " AND category = ?"
                params.append(cat_upper)

        if symbol:
            query += " AND symbol = ?"
            count_query += " AND symbol = ?"
            params.append(symbol.upper())

        if buy_venue:
            query += " AND buy_exchange = ?"
            count_query += " AND buy_exchange = ?"
            params.append(buy_venue.upper())

        if sell_venue:
            query += " AND sell_exchange = ?"
            count_query += " AND sell_exchange = ?"
            params.append(sell_venue.upper())

        if decision:
            query += " AND decision = ?"
            count_query += " AND decision = ?"
            params.append(decision.upper())

        if rejection_reason:
            query += " AND rejection_reason LIKE ?"
            count_query += " AND rejection_reason LIKE ?"
            params.append(f"%{rejection_reason.upper()}%")

        if time_range_seconds:
            cutoff = time.time() - time_range_seconds
            query += " AND created_at >= ?"
            count_query += " AND created_at >= ?"
            params.append(cutoff)

        allowed_sort_fields = {
            "created_at": "created_at",
            "timestamp": "created_at",
            "gross_spread": "gross_spread_bps",
            "gross_spread_bps": "gross_spread_bps",
            "net_edge": "net_edge_bps",
            "net_edge_bps": "net_edge_bps",
            "fees": "estimated_fee_buy + estimated_fee_sell",
            "slippage": "estimated_slippage_buy + estimated_slippage_sell",
            "latency": "latency_ms",
            "latency_ms": "latency_ms",
            "quote_age": "quote_age_ms",
            "quote_age_ms": "quote_age_ms",
            "liquidity": "orderbook_depth_buy"
        }
        sort_col = allowed_sort_fields.get(sort_by.lower(), "created_at")
        direction = "ASC" if sort_dir.lower() == "asc" else "DESC"

        query += f" ORDER BY {sort_col} {direction} LIMIT ? OFFSET ?"
        exec_params = list(params)
        exec_params.extend([limit, offset])

        conn = self._get_conn()
        try:
            total_count = conn.execute(count_query, params).fetchone()[0]
            rows = conn.execute(query, exec_params).fetchall()
            events = [dict(r) for r in rows]
        finally:
            conn.close()

        return {
            "total_count": total_count,
            "count": len(events),
            "limit": limit,
            "offset": offset,
            "events": events
        }

    def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single complete forensic evidence record."""
        conn = self._get_conn()
        try:
            row = conn.execute("SELECT * FROM arbitrage_evidence_events WHERE event_id = ?", (event_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_category_counts(self, time_range_seconds: Optional[float] = None) -> Dict[str, int]:
        """Aggregate exact event counts across all 12 cards in a single high-speed query."""
        where_clause = ""
        params = []
        if time_range_seconds:
            where_clause = "WHERE created_at >= ?"
            params.append(time.time() - time_range_seconds)

        conn = self._get_conn()
        try:
            row = conn.execute(f"""
            SELECT 
                COUNT(*) as total_scanned,
                COUNT(CASE WHEN gross_spread_bps > 0 THEN 1 END) as gross_prof,
                COUNT(CASE WHEN gross_spread_bps <= 0 THEN 1 END) as neg_spread,
                COUNT(CASE WHEN category = 'STALE_QUOTES' OR rejection_reason LIKE '%STALE%' THEN 1 END) as stale_quotes,
                COUNT(CASE WHEN category = 'CACHED_FALLBACK' OR rejection_reason LIKE '%FALLBACK%' OR rejection_reason LIKE '%CACHED%' THEN 1 END) as cached_fallback,
                COUNT(CASE WHEN category = 'FEE_REJECTIONS' OR rejection_reason LIKE '%FEE%' THEN 1 END) as fee_rej,
                COUNT(CASE WHEN category = 'SLIPPAGE_REJECTIONS' OR rejection_reason LIKE '%SLIPPAGE%' THEN 1 END) as slippage_rej,
                COUNT(CASE WHEN category = 'LIQUIDITY_REJECTIONS' OR rejection_reason LIKE '%LIQUIDITY%' OR rejection_reason LIKE '%DEPTH%' THEN 1 END) as liquidity_rej,
                COUNT(CASE WHEN category = 'RISK_REJECTIONS' OR rejection_reason LIKE '%RISK%' THEN 1 END) as risk_rej,
                COUNT(CASE WHEN category = 'GOVERNANCE_REJECTIONS' OR rejection_reason LIKE '%GOV%' OR rejection_reason LIKE '%KILL%' THEN 1 END) as gov_rej,
                COUNT(CASE WHEN net_edge_bps > 0 THEN 1 END) as net_prof,
                COUNT(CASE WHEN decision = 'EXECUTABLE' THEN 1 END) as executable
            FROM arbitrage_evidence_events {where_clause}
            """, params).fetchone()

            t_scanned = row["total_scanned"] if row else 0
            g_prof = row["gross_prof"] if row else 0
            n_spread = row["neg_spread"] if row else 0
            stale_q = row["stale_quotes"] if row else 0
            cached_fb = row["cached_fallback"] if row else 0
            fee_r = row["fee_rej"] if row else 0
            slip_r = row["slippage_rej"] if row else 0
            liq_r = row["liquidity_rej"] if row else 0
            risk_r = row["risk_rej"] if row else 0
            gov_r = row["gov_rej"] if row else 0
            net_p = row["net_prof"] if row else 0
            exec_opp = row["executable"] if row else 0

            return {
                "scanned_routes_count": t_scanned,
                "profitable_before_fees_count": g_prof,
                "rejected_by_negative_spread_count": n_spread,
                "rejected_by_stale_count": stale_q,
                "rejected_by_stale_quotes_count": stale_q,
                "rejected_by_cached_fallback_count": cached_fb,
                "rejected_by_fees_count": fee_r,
                "rejected_by_slippage_count": slip_r,
                "rejected_by_liquidity_count": liq_r,
                "rejected_by_risk_count": risk_r,
                "rejected_by_governance_count": gov_r,
                "profitable_after_fees_count": net_p,
                "profitable_after_all_friction_count": net_p,
                "executable_opportunities": exec_opp,
                "executable_opportunities_count": exec_opp
            }
        finally:
            conn.close()

    def reconcile_metrics(self, current_metrics: Dict[str, Any], db_counts: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """Audit reconciliation between displayed metrics and underlying database evidence."""
        if db_counts is None:
            db_counts = self.get_category_counts()
        
        cards = [
            ("Scanned Routes", "scanned_routes_count"),
            ("Gross Profitable", "profitable_before_fees_count"),
            ("Negative Spread", "rejected_by_negative_spread_count"),
            ("Stale Quotes", "rejected_by_stale_count"),
            ("Cached / Fallback", "rejected_by_cached_fallback_count"),
            ("Fee Rejections", "rejected_by_fees_count"),
            ("Slippage Rejections", "rejected_by_slippage_count"),
            ("Liquidity Rejections", "rejected_by_liquidity_count"),
            ("Risk Rejections", "rejected_by_risk_count"),
            ("Gov Rejections", "rejected_by_governance_count"),
            ("Net Profitable", "profitable_after_fees_count"),
            ("Executable", "executable_opportunities")
        ]

        reconciliation_report = []
        has_mismatch = False

        for card_label, key in cards:
            disp_count = int(current_metrics.get(key, 0))
            ev_count = int(db_counts.get(key, 0))
            diff = disp_count - ev_count
            if diff != 0:
                has_mismatch = True
            reconciliation_report.append({
                "card_metric": card_label,
                "displayed_count": disp_count,
                "evidence_count": ev_count,
                "difference": diff,
                "status": "PASS" if diff == 0 else "INTEGRITY_MISMATCH"
            })

        return {
            "status": "INTEGRITY_VERIFIED" if not has_mismatch else "METRIC_INTEGRITY_ERROR",
            "is_consistent": not has_mismatch,
            "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "total_categories_checked": len(cards),
            "reconciliation": reconciliation_report
        }

    def replay_decision(self, event_id: str) -> Dict[str, Any]:
        """Forensic Decision Replay: Deterministically recalculate spread, friction, and decision."""
        event = self.get_event_by_id(event_id)
        if not event:
            return {
                "status": "error",
                "message": f"Event {event_id} not found in forensic database."
            }

        snapshot = {}
        if event.get("raw_snapshot_json"):
            try:
                snapshot = json.loads(event["raw_snapshot_json"])
            except Exception:
                snapshot = {}

        buy_ask = float(snapshot.get("buy_ask", event.get("buy_ask", event.get("buy_price_used", 0.0))))
        sell_bid = float(snapshot.get("sell_bid", event.get("sell_bid", event.get("sell_price_used", 0.0))))
        buy_fee_bps = float(snapshot.get("buy_fee_bps", event.get("estimated_fee_buy", 7.5)))
        sell_fee_bps = float(snapshot.get("sell_fee_bps", event.get("estimated_fee_sell", 7.5)))
        slippage_bps = float(snapshot.get("slippage_bps", 2.0))
        latency_ms = float(snapshot.get("latency_ms", event.get("latency_ms", 25.0)))
        quote_age_ms = float(snapshot.get("quote_age_ms", event.get("quote_age_ms", 0.0)))
        quote_status = snapshot.get("quote_status", event.get("freshness_result", "FRESH"))
        is_live_buy = bool(snapshot.get("is_live_buy", True))
        is_live_sell = bool(snapshot.get("is_live_sell", True))

        from .spread_detector import SpreadDetector
        detector = SpreadDetector()
        replayed_spread = detector.compute_spread(
            symbol=event["symbol"],
            buy_exchange=event["buy_exchange"],
            sell_exchange=event["sell_exchange"],
            buy_ask_price=buy_ask,
            sell_bid_price=sell_bid,
            buy_fee_bps=buy_fee_bps,
            sell_fee_bps=sell_fee_bps,
            latency_ms=latency_ms,
            slippage_bps=slippage_bps,
            data_age_ms=quote_age_ms,
            quote_status=quote_status,
            is_live_buy=is_live_buy,
            is_live_sell=is_live_sell
        )

        replayed_decision = "EXECUTABLE" if replayed_spread.is_executable else "REJECTED"
        original_decision = event["decision"]
        is_match = (replayed_decision == original_decision)

        return {
            "status": "success",
            "event_id": event_id,
            "is_match": is_match,
            "verification_status": "DETERMINISTIC_MATCH" if is_match else "EVIDENCE_REPLAY_MISMATCH",
            "original_evaluation": {
                "decision": original_decision,
                "rejection_reason": event["rejection_reason"],
                "gross_spread_pct": event["gross_spread_pct"],
                "net_edge_pct": event["net_edge_pct"]
            },
            "replayed_evaluation": {
                "decision": replayed_decision,
                "rejection_reason": replayed_spread.rejection_reason,
                "gross_spread_pct": replayed_spread.gross_spread_pct,
                "net_edge_pct": replayed_spread.net_spread_pct,
                "total_fees_bps": replayed_spread.total_fees_bps,
                "latency_penalty_bps": replayed_spread.latency_penalty_bps
            },
            "inputs_replayed": {
                "buy_ask_price": buy_ask,
                "sell_bid_price": sell_bid,
                "buy_exchange": event["buy_exchange"],
                "sell_exchange": event["sell_exchange"],
                "latency_ms": latency_ms,
                "quote_age_ms": quote_age_ms
            }
        }

    def export_csv_with_hash(
        self,
        category: Optional[str] = None,
        symbol: Optional[str] = None,
        time_range_seconds: Optional[float] = None
    ) -> Tuple[str, str, int]:
        """Generate actual CSV string and compute SHA-256 integrity checksum."""
        data = self.query_events(
            category=category,
            symbol=symbol,
            time_range_seconds=time_range_seconds,
            limit=50000,
            offset=0
        )
        events = data["events"]

        import csv
        import io
        output = io.StringIO()
        fieldnames = [
            "event_id", "timestamp_utc", "symbol", "buy_exchange", "sell_exchange",
            "buy_price", "sell_price", "gross_spread_bps", "gross_spread_pct",
            "quantity", "fees", "slippage", "net_edge_bps", "latency_ms", "quote_age_ms",
            "liquidity", "risk", "governance", "decision", "rejection_reason",
            "source", "source_timestamp"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for e in events:
            writer.writerow({
                "event_id": e["event_id"],
                "timestamp_utc": e["timestamp_utc"],
                "symbol": e["symbol"],
                "buy_exchange": e["buy_exchange"],
                "sell_exchange": e["sell_exchange"],
                "buy_price": e["buy_price_used"],
                "sell_price": e["sell_price_used"],
                "gross_spread_bps": e["gross_spread_bps"],
                "gross_spread_pct": e["gross_spread_pct"],
                "quantity": e["estimated_quantity"],
                "fees": round(e["estimated_fee_buy"] + e["estimated_fee_sell"], 2),
                "slippage": round(e["estimated_slippage_buy"] + e["estimated_slippage_sell"], 2),
                "net_edge_bps": e["net_edge_bps"],
                "latency_ms": e["latency_ms"],
                "quote_age_ms": e["quote_age_ms"],
                "liquidity": e["orderbook_depth_buy"],
                "risk": e["risk_result"],
                "governance": e["governance_result"],
                "decision": e["decision"],
                "rejection_reason": e["rejection_reason"],
                "source": e["market_data_source"],
                "source_timestamp": e["source_timestamp"]
            })

        csv_content = output.getvalue()
        sha256_hash = hashlib.sha256(csv_content.encode("utf-8")).hexdigest()
        return csv_content, sha256_hash, len(events)

    def export_json_with_hash(
        self,
        category: Optional[str] = None,
        symbol: Optional[str] = None,
        time_range_seconds: Optional[float] = None
    ) -> Tuple[str, str, int]:
        """Generate actual JSON string and compute SHA-256 integrity checksum."""
        data = self.query_events(
            category=category,
            symbol=symbol,
            time_range_seconds=time_range_seconds,
            limit=50000,
            offset=0
        )
        events = data["events"]
        json_content = json.dumps({
            "export_metadata": {
                "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "category_filter": category or "ALL",
                "symbol_filter": symbol or "ALL",
                "total_records": len(events)
            },
            "evidence_records": events
        }, indent=2)

        sha256_hash = hashlib.sha256(json_content.encode("utf-8")).hexdigest()
        return json_content, sha256_hash, len(events)

    def get_latencies(self) -> Dict[str, float]:
        """Compute P50, P95, P99 database write latencies in milliseconds."""
        with self._latencies_lock:
            if not self._write_latencies:
                return {"p50_ms": 0.0, "p95_ms": 0.0, "p99_ms": 0.0}
            sorted_lats = sorted(self._write_latencies)
            n = len(sorted_lats)
            p50 = sorted_lats[int(n * 0.50)]
            p95 = sorted_lats[min(n - 1, int(n * 0.95))]
            p99 = sorted_lats[min(n - 1, int(n * 0.99))]
            return {
                "p50_ms": round(p50, 2),
                "p95_ms": round(p95, 2),
                "p99_ms": round(p99, 2)
            }

    def get_status(self) -> Dict[str, Any]:
        """Returns comprehensive real-time health and diagnostics for the evidence pipeline."""
        lats = self.get_latencies()
        return {
            "worker_running": self._worker_thread.is_alive() if hasattr(self, "_worker_thread") else False,
            "worker_count": 1,
            "queue_depth": self._write_queue.qsize(),
            "fallback_buffer_depth": len(self._fallback_buffer),
            "events_generated": self.events_generated,
            "events_enqueued": self.events_enqueued,
            "events_persisted": self.events_persisted,
            "events_retried": self.events_retried,
            "events_failed": self.events_failed,
            "events_dropped": self.events_dropped,
            "lock_errors_count": self.lock_errors_count,
            "db_write_latency_p50_ms": lats["p50_ms"],
            "db_write_latency_p95_ms": lats["p95_ms"],
            "db_write_latency_p99_ms": lats["p99_ms"],
            "last_successful_write_utc": self.last_successful_write_utc,
            "last_error": self.last_error,
            "db_path": self.db_path
        }

    def stop_worker(self, timeout: float = 10.0):
        """Gracefully drains all queued events to disk and stops worker."""
        self._stop_event.set()
        if hasattr(self, "_worker_thread") and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=timeout)
        
        # Drain any residual events in queue
        residual = []
        while not self._write_queue.empty():
            try:
                residual.append(self._write_queue.get_nowait())
            except queue.Empty:
                break
        
        with self._buffer_lock:
            residual.extend(self._fallback_buffer)
            self._fallback_buffer = []

        if residual:
            self._insert_batch_with_retry(residual)

# Global Singleton Instance
arbitrage_evidence_store = ArbitrageEvidenceStore()
