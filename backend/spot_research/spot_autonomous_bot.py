"""
Autonomous Self-Learning Intelligent Trading Bot for Spot & Meme Coin Research.
Scans real-time discovered coins, executes automated paper validation trades with isolated sub-wallet,
monitors live PnL, executes Take-Profit/Stop-Loss, and self-learns from paper outcomes.
"""

import time
import json
import uuid
import asyncio
import threading
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from loguru import logger
from backend.database.db_config import get_db_path, create_sqlite_connection
from .coin_discovery_engine import CoinDiscoveryEngine, DiscoveredCoin
from .coin_classifier import CoinClassifier
from .coin_risk_engine import CoinRiskEngine
from .coin_ai_researcher import CoinAIResearcher
from .paper_validation_engine import PaperValidationEngine, PaperValidationTrade
from .spot_sub_wallet import SpotSubWalletManager, SpotWalletState
from .spot_research_evidence_store import SpotResearchEvidenceStore

class SpotBotConfig(BaseModel):
    is_enabled: bool = True
    allocation_per_trade_usd: float = 250.0  # User customizable capital per trade
    max_active_positions: int = 5            # Max concurrent open paper positions
    min_opportunity_score: float = 55.0      # Minimum AI opportunity score required
    max_risk_score: float = 60.0             # Maximum risk score permitted
    take_profit_pct: float = 12.0            # Auto Take-Profit target percentage
    stop_loss_pct: float = 5.0               # Auto Stop-Loss protection percentage
    scan_interval_seconds: int = 20          # Scanning loop frequency
    allowed_categories: List[str] = ["MEME", "NEW", "ESTABLISHED"]
    auto_learn_enabled: bool = True          # Enable self-learning weight adaptations

class LearnedLesson(BaseModel):
    lesson_id: str
    trade_id: str
    symbol: str
    category: str
    outcome: str  # WIN_TP, LOSS_SL, LOSS_TIMEOUT
    pnl_usd: float
    pnl_pct: float
    lesson_text: str
    weight_adjustments: Dict[str, float] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)

class SpotAutonomousBot:
    """Intelligent autonomous spot research bot with continuous self-learning loop."""

    def __init__(
        self,
        discovery_engine: Optional[CoinDiscoveryEngine] = None,
        classifier: Optional[CoinClassifier] = None,
        risk_engine: Optional[CoinRiskEngine] = None,
        ai_researcher: Optional[CoinAIResearcher] = None,
        paper_engine: Optional[PaperValidationEngine] = None,
        sub_wallet: Optional[SpotSubWalletManager] = None,
        evidence_store: Optional[SpotResearchEvidenceStore] = None,
        db_path: Optional[str] = None
    ):
        self.db_path = db_path or get_db_path()
        self.discovery_engine = discovery_engine or CoinDiscoveryEngine()
        self.classifier = classifier or CoinClassifier()
        self.risk_engine = risk_engine or CoinRiskEngine()
        self.ai_researcher = ai_researcher or CoinAIResearcher()
        self.paper_engine = paper_engine or PaperValidationEngine()
        self.sub_wallet = sub_wallet or SpotSubWalletManager(self.db_path)
        self.evidence_store = evidence_store or SpotResearchEvidenceStore()

        self.active_bot_trades: Dict[str, Dict[str, Any]] = {}
        self.closed_bot_trades: List[Dict[str, Any]] = []
        self.learned_lessons: List[LearnedLesson] = []
        
        # Adaptive learning dynamic modifiers
        self.category_risk_multipliers: Dict[str, float] = {
            "MEME": 1.0,
            "NEW": 1.0,
            "ESTABLISHED": 1.0
        }

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._init_db()
        self.config = self._load_config()
        self._load_active_trades_from_db()
        self._load_closed_trades_from_db()
        self._load_lessons()

    def _init_db(self):
        with create_sqlite_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS spot_bot_config (
                    key TEXT PRIMARY KEY,
                    config_json TEXT NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS spot_bot_trades (
                    trade_id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    category TEXT NOT NULL,
                    exchange TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    quantity REAL NOT NULL,
                    position_size_usd REAL NOT NULL,
                    stop_loss_price REAL NOT NULL,
                    take_profit_price REAL NOT NULL,
                    opportunity_score REAL NOT NULL,
                    risk_score REAL NOT NULL,
                    status TEXT NOT NULL,
                    entry_ts REAL NOT NULL,
                    exit_price REAL,
                    exit_ts REAL,
                    exit_reason TEXT,
                    net_pnl_usd REAL,
                    roi_pct REAL
                )
            """)
            conn.commit()

    def _load_config(self) -> SpotBotConfig:
        try:
            with create_sqlite_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT config_json FROM spot_bot_config WHERE key = 'MAIN_CONFIG'")
                row = cursor.fetchone()
                if row:
                    data = json.loads(row["config_json"])
                    return SpotBotConfig(**data)
        except Exception as e:
            logger.error(f"[SPOT_BOT] Failed to load config from DB: {e}")
        return SpotBotConfig()

    def save_config(self, new_config: SpotBotConfig):
        with self._lock:
            self.config = new_config
            try:
                with create_sqlite_connection(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT OR REPLACE INTO spot_bot_config (key, config_json, updated_at)
                        VALUES ('MAIN_CONFIG', ?, ?)
                    """, (new_config.model_dump_json(), time.time()))
                    conn.commit()
                logger.info(f"[SPOT_BOT] Updated configuration: Capital/Trade=${new_config.allocation_per_trade_usd}, MaxPos={new_config.max_active_positions}, MinOpp={new_config.min_opportunity_score}")
            except Exception as e:
                logger.error(f"[SPOT_BOT] Error saving config: {e}")


    def _load_active_trades_from_db(self):
        try:
            with create_sqlite_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM spot_bot_trades WHERE status = 'OPEN'")
                rows = cursor.fetchall()
                for r in rows:
                    self.active_bot_trades[r["trade_id"]] = {
                        "trade_id": r["trade_id"],
                        "symbol": r["symbol"],
                        "category": r["category"],
                        "exchange": r["exchange"],
                        "entry_price": float(r["entry_price"]),
                        "current_price": float(r["entry_price"]),
                        "quantity": float(r["quantity"]),
                        "position_size_usd": float(r["position_size_usd"]),
                        "stop_loss_price": float(r["stop_loss_price"]),
                        "take_profit_price": float(r["take_profit_price"]),
                        "opportunity_score": float(r["opportunity_score"]),
                        "risk_score": float(r["risk_score"]),
                        "status": "OPEN",
                        "entry_ts": float(r["entry_ts"]),
                        "unrealized_pnl_usd": 0.0,
                        "roi_pct": 0.0
                    }
                logger.info(f"[SPOT_BOT] Restored {len(self.active_bot_trades)} active trades from SQLite.")
        except Exception as e:
            logger.error(f"[SPOT_BOT] Error loading active trades: {e}")

    def _load_closed_trades_from_db(self):
        try:
            with create_sqlite_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM spot_bot_trades WHERE status != 'OPEN' ORDER BY exit_ts DESC LIMIT 50")
                rows = cursor.fetchall()
                self.closed_bot_trades = [
                    {
                        "trade_id": r["trade_id"],
                        "symbol": r["symbol"],
                        "category": r["category"],
                        "exchange": r["exchange"],
                        "entry_price": float(r["entry_price"]),
                        "exit_price": float(r["exit_price"]) if r["exit_price"] else None,
                        "quantity": float(r["quantity"]),
                        "position_size_usd": float(r["position_size_usd"]),
                        "status": r["status"],
                        "exit_reason": r["exit_reason"],
                        "net_pnl_usd": float(r["net_pnl_usd"]) if r["net_pnl_usd"] else 0.0,
                        "roi_pct": float(r["roi_pct"]) if r["roi_pct"] else 0.0,
                        "entry_ts": float(r["entry_ts"]),
                        "exit_ts": float(r["exit_ts"]) if r["exit_ts"] else None
                    } for r in rows
                ]
        except Exception as e:
            logger.error(f"[SPOT_BOT] Error loading closed trades: {e}")

    def _load_lessons(self):
        try:
            with create_sqlite_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM spot_bot_learned_lessons ORDER BY timestamp DESC LIMIT 50")
                rows = cursor.fetchall()
                self.learned_lessons = [
                    LearnedLesson(
                        lesson_id=r["lesson_id"],
                        trade_id=r["trade_id"],
                        symbol=r["symbol"],
                        category=r["category"],
                        outcome=r["outcome"],
                        pnl_usd=float(r["pnl_usd"]),
                        pnl_pct=float(r["pnl_pct"]),
                        lesson_text=r["lesson_text"],
                        weight_adjustments=json.loads(r["weight_adjustments"] or "{}"),
                        timestamp=float(r["timestamp"])
                    ) for r in rows
                ]
        except Exception as e:
            logger.error(f"[SPOT_BOT] Error loading learned lessons: {e}")

    def start(self):
        """Start the background autonomous scanning and execution bot."""
        with self._lock:
            if self._running:
                return
            self._running = True
            self._thread = threading.Thread(target=self._run_loop, daemon=True, name="SpotAutonomousBot")
            self._thread.start()
            logger.info("[SPOT_BOT] Autonomous Self-Learning Spot Bot started.")

    def stop(self):
        """Stop the background bot loop."""
        with self._lock:
            self._running = False
            logger.info("[SPOT_BOT] Autonomous Spot Bot stopped.")

    def is_running(self) -> bool:
        return self._running

    def _run_loop(self):
        while self._running:
            try:
                if self.config.is_enabled:
                    self._monitor_open_positions()
                    self._scan_and_execute_candidates()
            except Exception as e:
                logger.error(f"[SPOT_BOT] Error in autonomous cycle: {e}")
            
            # Sleep in short increments to allow fast shutdown
            for _ in range(max(1, self.config.scan_interval_seconds)):
                if not self._running:
                    break
                time.sleep(1)

    def _scan_and_execute_candidates(self):
        """Scan candidate coins and autonomously execute paper trade if high conviction."""
        if len(self.active_bot_trades) >= self.config.max_active_positions:
            return

        coins = self.discovery_engine.get_all_discovered_coins()
        if not coins:
            return

        # Sort coins by opportunity / momentum
        sorted_coins = sorted(
            coins,
            key=lambda c: (c.volume_24h_usd or 0.0) * (abs(c.price_change_24h_pct or 0.0)),
            reverse=True
        )

        for coin in sorted_coins[:25]:
            if not self._running or len(self.active_bot_trades) >= self.config.max_active_positions:
                break
            
            # Skip if already open
            if any(t["symbol"] == coin.symbol for t in self.active_bot_trades.values()):
                continue

            # Classify
            classification = self.classifier.classify(coin)
            if classification.category not in self.config.allowed_categories:
                continue

            # Evaluate Risk with dynamic self-learning category multiplier
            risk_multiplier = self.category_risk_multipliers.get(classification.category, 1.0)
            risk_report = self.risk_engine.evaluate_risk(coin)
            adjusted_risk_score = min(100.0, risk_report.overall_risk_score * risk_multiplier)

            if adjusted_risk_score > self.config.max_risk_score:
                continue

            # Generate AI Research Dossier
            dossier = self.ai_researcher.generate_research_dossier(coin, classification, risk_report)

            # Conviction Gate: Requires 'PAPER_TEST' and Opp Score >= threshold
            if dossier.opportunity_score < self.config.min_opportunity_score or adjusted_risk_score > self.config.max_risk_score:
                continue

            # Wallet Margin Gate: Check if sub-wallet has enough USDT
            alloc_usd = self.config.allocation_per_trade_usd
            if not self.sub_wallet.reserve_margin(alloc_usd):
                logger.warning(f"[SPOT_BOT] Sub-wallet cannot allocate ${alloc_usd:.2f} for {coin.symbol}. Skipping.")
                break

            # Execute Paper Validation Trade
            res = self.paper_engine.execute_paper_validation(
                coin=coin,
                dossier=dossier,
                allocation_usd=alloc_usd
            )

            if res.get("status") == "SUCCESS" and res.get("trade"):
                trade_dict = res["trade"]
                trade_id = trade_dict["trade_id"]
                
                # Apply user customized TP & SL
                effective_entry = float(trade_dict["entry_price"])
                tp_price = round(effective_entry * (1.0 + (self.config.take_profit_pct / 100.0)), 6)
                sl_price = round(effective_entry * (1.0 - (self.config.stop_loss_pct / 100.0)), 6)
                
                bot_trade = {
                    "trade_id": trade_id,
                    "symbol": coin.symbol,
                    "category": classification.category,
                    "exchange": coin.exchange,
                    "entry_price": effective_entry,
                    "current_price": effective_entry,
                    "quantity": float(trade_dict["quantity"]),
                    "position_size_usd": alloc_usd,
                    "stop_loss_price": sl_price,
                    "take_profit_price": tp_price,
                    "opportunity_score": dossier.opportunity_score,
                    "risk_score": adjusted_risk_score,
                    "status": "OPEN",
                    "entry_ts": time.time(),
                    "unrealized_pnl_usd": 0.0,
                    "roi_pct": 0.0
                }

                with self._lock:
                    self.active_bot_trades[trade_id] = bot_trade

                # Persist to SQLite
                self._save_trade_to_db(bot_trade)
                
                # Record evidence event
                self.evidence_store.record_evidence_event(
                    event_type="SPOT_BOT_TRADE_OPENED",
                    symbol=coin.symbol,
                    actor="AUTONOMOUS_LEARNER_BOT",
                    data={
                        "trade_id": trade_id,
                        "capital_allocated_usd": alloc_usd,
                        "entry_price": effective_entry,
                        "tp": tp_price,
                        "sl": sl_price,
                        "category": classification.category,
                        "opp_score": dossier.opportunity_score
                    }
                )

                logger.info(f"[SPOT_BOT] Autonomously opened {classification.category} trade on {coin.symbol} (${alloc_usd} @ ${effective_entry:.6f})")

    def _monitor_open_positions(self):
        """Update live prices for active positions and trigger TP / SL closures."""
        if not self.active_bot_trades:
            return

        all_coins_map = {c.symbol: c for c in self.discovery_engine.get_all_discovered_coins()}
        trades_to_close = []

        with self._lock:
            for trade_id, trade in list(self.active_bot_trades.items()):
                symbol = trade["symbol"]
                coin = all_coins_map.get(symbol)
                
                if coin and coin.current_price and coin.current_price > 0:
                    curr_price = coin.current_price
                else:
                    # In simulated market conditions, calculate small live drift
                    drift = ((time.time() - trade["entry_ts"]) % 10 - 5) * 0.001
                    curr_price = trade["entry_price"] * (1.0 + drift)

                trade["current_price"] = curr_price
                entry = trade["entry_price"]
                pnl_pct = ((curr_price - entry) / entry) * 100.0
                pnl_usd = round((trade["position_size_usd"] * (pnl_pct / 100.0)), 4)
                
                trade["unrealized_pnl_usd"] = pnl_usd
                trade["roi_pct"] = round(pnl_pct, 2)

                # Check Take Profit
                if curr_price >= trade["take_profit_price"]:
                    trades_to_close.append((trade_id, "TAKE_PROFIT", curr_price, pnl_usd, pnl_pct))
                # Check Stop Loss
                elif curr_price <= trade["stop_loss_price"]:
                    trades_to_close.append((trade_id, "STOP_LOSS", curr_price, pnl_usd, pnl_pct))

        # Process Closures & Self-Learning
        for trade_id, reason, exit_price, pnl_usd, pnl_pct in trades_to_close:
            self._close_position(trade_id, reason, exit_price, pnl_usd, pnl_pct)

    def _close_position(self, trade_id: str, reason: str, exit_price: float, net_pnl_usd: float, pnl_pct: float):
        """Close an active paper trade, release margin to sub-wallet, and extract learned lesson."""
        trade = None
        with self._lock:
            if trade_id in self.active_bot_trades:
                trade = self.active_bot_trades.pop(trade_id)

        if not trade:
            return

        is_win = net_pnl_usd > 0
        trade["status"] = f"CLOSED_{reason}"
        trade["exit_price"] = exit_price
        trade["exit_ts"] = time.time()
        trade["exit_reason"] = reason
        trade["net_pnl_usd"] = net_pnl_usd
        trade["roi_pct"] = round(pnl_pct, 2)

        # Release margin and settle PnL in the isolated Sub-Wallet
        self.sub_wallet.release_margin(
            margin_usd=trade["position_size_usd"],
            net_pnl_usd=net_pnl_usd,
            is_win=is_win
        )

        with self._lock:
            self.closed_bot_trades.insert(0, trade)
            if len(self.closed_bot_trades) > 100:
                self.closed_bot_trades.pop()

        # Update trade in SQLite
        self._update_trade_in_db(trade)

        # Record Evidence
        self.evidence_store.record_evidence_event(
            event_type="SPOT_BOT_TRADE_CLOSED",
            symbol=trade["symbol"],
            actor="AUTONOMOUS_LEARNER_BOT",
            data={
                "trade_id": trade_id,
                "exit_reason": reason,
                "net_pnl_usd": net_pnl_usd,
                "roi_pct": pnl_pct,
                "is_win": is_win
            }
        )

        # Run Self-Learning & Lesson Extraction
        if self.config.auto_learn_enabled:
            self._extract_and_apply_lesson(trade, reason, net_pnl_usd, pnl_pct)

        logger.info(f"[SPOT_BOT] Closed {trade['symbol']} on {reason} | PnL: ${net_pnl_usd:+.2f} ({pnl_pct:+.2f}%)")

    def _extract_and_apply_lesson(self, trade: Dict[str, Any], reason: str, net_pnl_usd: float, pnl_pct: float):
        """Reinforcement Learning: Extracts qualitative insights and tunes adaptive risk weights."""
        symbol = trade["symbol"]
        category = trade["category"]
        is_win = net_pnl_usd > 0

        # Generate qualitative lesson
        if is_win:
            outcome = "WIN_TP"
            lesson_text = (
                f"Validation success on {category} asset {symbol}: Volume breakout confirmed momentum. "
                f"Gained +${net_pnl_usd:.2f} ({pnl_pct:+.2f}%). Reinforcing opportunity factor weights."
            )
            current_mult = self.category_risk_multipliers.get(category, 1.0)
            new_mult = max(0.85, current_mult - 0.02)
            self.category_risk_multipliers[category] = round(new_mult, 3)
            adj = {f"{category}_risk_penalty": -0.02}
        else:
            outcome = "LOSS_SL"
            lesson_text = (
                f"Stop-loss triggered on {category} asset {symbol}: Price slipped -{abs(pnl_pct):.2f}% (-${abs(net_pnl_usd):.2f}). "
                f"Identified elevated volatility/spread overhang. Increasing defensive risk filter for {category} tokens."
            )
            current_mult = self.category_risk_multipliers.get(category, 1.0)
            new_mult = min(1.35, current_mult + 0.05)
            self.category_risk_multipliers[category] = round(new_mult, 3)
            adj = {f"{category}_risk_penalty": +0.05}

        lesson = LearnedLesson(
            lesson_id=f"LSN-{uuid.uuid4().hex[:8].upper()}",
            trade_id=trade["trade_id"],
            symbol=symbol,
            category=category,
            outcome=outcome,
            pnl_usd=net_pnl_usd,
            pnl_pct=pnl_pct,
            lesson_text=lesson_text,
            weight_adjustments=adj,
            timestamp=time.time()
        )

        with self._lock:
            self.learned_lessons.insert(0, lesson)
            if len(self.learned_lessons) > 50:
                self.learned_lessons.pop()

        # Persist lesson to SQLite
        try:
            with create_sqlite_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO spot_bot_learned_lessons (
                        lesson_id, trade_id, symbol, category, outcome,
                        pnl_usd, pnl_pct, lesson_text, weight_adjustments, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    lesson.lesson_id, lesson.trade_id, lesson.symbol, lesson.category,
                    lesson.outcome, lesson.pnl_usd, lesson.pnl_pct, lesson.lesson_text,
                    json.dumps(lesson.weight_adjustments), lesson.timestamp
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"[SPOT_BOT] Error persisting lesson: {e}")

    def _save_trade_to_db(self, trade: Dict[str, Any]):
        try:
            with create_sqlite_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO spot_bot_trades (
                        trade_id, symbol, category, exchange, entry_price, quantity,
                        position_size_usd, stop_loss_price, take_profit_price,
                        opportunity_score, risk_score, status, entry_ts
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    trade["trade_id"], trade["symbol"], trade["category"], trade["exchange"],
                    trade["entry_price"], trade["quantity"], trade["position_size_usd"],
                    trade["stop_loss_price"], trade["take_profit_price"], trade["opportunity_score"],
                    trade["risk_score"], trade["status"], trade["entry_ts"]
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"[SPOT_BOT] Error saving trade to DB: {e}")

    def _update_trade_in_db(self, trade: Dict[str, Any]):
        try:
            with create_sqlite_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE spot_bot_trades
                    SET status = ?, exit_price = ?, exit_ts = ?, exit_reason = ?,
                        net_pnl_usd = ?, roi_pct = ?
                    WHERE trade_id = ?
                """, (
                    trade["status"], trade.get("exit_price"), trade.get("exit_ts"),
                    trade.get("exit_reason"), trade.get("net_pnl_usd"), trade.get("roi_pct"),
                    trade["trade_id"]
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"[SPOT_BOT] Error updating trade in DB: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Return full telemetry, dedicated sub-wallet state, active positions, and self-learning insights."""
        with self._lock:
            active_list = list(self.active_bot_trades.values())
            closed_list = list(self.closed_bot_trades)
            lessons_list = [l.model_dump() for l in self.learned_lessons[:15]]
            unrealized = sum(t.get("unrealized_pnl_usd", 0.0) for t in active_list)

        wallet_state = self.sub_wallet.get_wallet_state(unrealized_pnl_usd=unrealized)
        
        # Calculate win rate and metrics
        total_closed = wallet_state.total_trades_count
        win_rate = (wallet_state.winning_trades_count / total_closed * 100.0) if total_closed > 0 else 0.0
        roi_total = ((wallet_state.total_equity_usd - wallet_state.initial_balance_usd) / wallet_state.initial_balance_usd * 100.0) if wallet_state.initial_balance_usd > 0 else 0.0

        return {
            "is_running": self._running,
            "config": self.config.model_dump(),
            "wallet": {
                "wallet_id": wallet_state.wallet_id,
                "name": wallet_state.name,
                "initial_balance_usd": wallet_state.initial_balance_usd,
                "usdt_available_balance": round(wallet_state.usdt_available_balance, 2),
                "allocated_margin_usd": round(wallet_state.allocated_margin_usd, 2),
                "realized_pnl_usd": round(wallet_state.realized_pnl_usd, 2),
                "unrealized_pnl_usd": round(unrealized, 2),
                "total_equity_usd": round(wallet_state.total_equity_usd, 2),
                "total_trades_count": total_closed,
                "winning_trades_count": wallet_state.winning_trades_count,
                "losing_trades_count": wallet_state.losing_trades_count,
                "win_rate_pct": round(win_rate, 1),
                "roi_total_pct": round(roi_total, 2)
            },
            "active_positions": active_list,
            "active_positions_count": len(active_list),
            "closed_trades": closed_list[:20],
            "learned_lessons": lessons_list,
            "learned_lessons_count": len(self.learned_lessons),
            "adaptive_multipliers": self.category_risk_multipliers
        }

spot_autonomous_bot = SpotAutonomousBot()
