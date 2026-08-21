import time
import threading
from typing import Dict, List, Any, Optional
from loguru import logger

from .cross_exchange_arbitrage_engine import CrossExchangeArbitrageEngine, CrossExchangeOpportunity, cross_exchange_engine
from .arbitrage_opportunity_ranker import ArbitrageOpportunityRanker
from .arbitrage_shadow_router import ArbitrageShadowRouter
from .arbitrage_metrics import ArbitrageMetricsTracker

class ArbitrageBackgroundScanner:
    """Continuous 24/7 Background Arbitrage Scanner Daemon.
    
    Runs independently of frontend traffic to continuously evaluate multi-venue orderbook
    depth, track realistic friction rejections, and update telemetry.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ArbitrageBackgroundScanner, cls).__new__(cls)
            cls._instance._init_scanner()
        return cls._instance

    def _init_scanner(self):
        self.engine = cross_exchange_engine
        self.ranker = ArbitrageOpportunityRanker()
        self.shadow_router = ArbitrageShadowRouter()
        
        self.symbols: List[str] = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "AVAX/USDT", "BNB/USDT"]
        self.interval_seconds: float = 2.0
        
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # In-memory cached latest state
        self.scanner_running: bool = False
        self.last_scan_timestamp: float = 0.0
        self.last_successful_scan: float = 0.0
        self.last_scan_duration_ms: float = 0.0
        self.last_scan_error: Optional[str] = None
        self.total_scans: int = 0
        
        self._cached_opportunities: Dict[str, List[CrossExchangeOpportunity]] = {}
        self._lock = threading.Lock()

    def start(self):
        """Start the background daemon thread if not already running."""
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                logger.info("[ArbitrageBackgroundScanner] Scanner thread already running.")
                return
            
            self._stop_event.clear()
            self.scanner_running = True
            self._thread = threading.Thread(target=self._run_loop, daemon=True, name="ArbitrageBackgroundScannerThread")
            self._thread.start()
            logger.info("[ArbitrageBackgroundScanner] Background 24/7 scanner thread started successfully.")

    def stop(self):
        """Gracefully stop the background scanner thread."""
        with self._lock:
            if not self.scanner_running:
                return
            self._stop_event.set()
            self.scanner_running = False
            logger.info("[ArbitrageBackgroundScanner] Stop event signaled.")

    def _run_loop(self):
        """Continuous execution loop."""
        while not self._stop_event.is_set():
            t_start = time.perf_counter()
            self.last_scan_timestamp = time.time()

            try:
                for sym in self.symbols:
                    if self._stop_event.is_set():
                        break
                    raw_opps = self.engine.scan_opportunities(symbol=sym)
                    ranked = self.ranker.rank_opportunities(raw_opps)
                    with self._lock:
                        self._cached_opportunities[sym] = ranked
                
                self.last_successful_scan = time.time()
                self.last_scan_duration_ms = round((time.perf_counter() - t_start) * 1000.0, 2)
                self.total_scans += 1
                self.last_scan_error = None

            except Exception as e:
                self.last_scan_error = str(e)
                logger.error(f"[ArbitrageBackgroundScanner] Error in scanner cycle: {e}")

            # Sleep until next cycle interval
            elapsed = time.perf_counter() - t_start
            sleep_time = max(0.2, self.interval_seconds - elapsed)
            self._stop_event.wait(timeout=sleep_time)

        self.scanner_running = False
        logger.info("[ArbitrageBackgroundScanner] Background scanner loop terminated cleanly.")

    def get_latest_opportunities(self, symbol: str = "BTC/USDT") -> List[CrossExchangeOpportunity]:
        """Fetch latest cached opportunities in sub-1ms without blocking the event loop."""
        with self._lock:
            return self._cached_opportunities.get(symbol, [])

    def get_telemetry(self) -> Dict[str, Any]:
        """Expose scanner health and heartbeat telemetry."""
        return {
            "scanner_running": self.scanner_running,
            "last_scan_timestamp": self.last_scan_timestamp,
            "last_successful_scan": self.last_successful_scan,
            "last_scan_duration_ms": self.last_scan_duration_ms,
            "last_scan_error": self.last_scan_error,
            "total_scans": self.total_scans,
            "symbols_monitored": self.symbols
        }

# Global Singleton
arbitrage_background_scanner = ArbitrageBackgroundScanner()
