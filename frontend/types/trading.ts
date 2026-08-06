export interface Position {
  id: string;
  symbol: string;
  side: "LONG" | "SHORT";
  entry_price: number;
  current_price: number;
  amount: number;
  leverage: number;
  margin_usd: number;
  unrealized_pnl_usd: number;
  unrealized_pnl_pct: number;
  stop_loss_price: number;
  take_profit_price: number;
  liquidation_price: number;
  entry_time: string;
}

export interface TradeRecord {
  id: string;
  symbol: string;
  side: "LONG" | "SHORT";
  entry_price: number;
  exit_price: number;
  amount: number;
  margin_usd: number;
  pnl_usd: number;
  pnl_pct: number;
  entry_time: string;
  exit_time: string;
  close_reason: string;
  status: "OPEN" | "CLOSED";
  strategy?: string;
  confidence?: number;
  reason?: string;
  exchange?: string;
  order_id?: string;
  entry_fee?: number;
  exit_fee?: number;
  funding_fee?: number;
  slippage?: number;
  latency?: number;
}

export interface WalletTransaction {
  id?: number;
  tx_id: string;
  timestamp: string;
  tx_type: "DEPOSIT" | "WITHDRAW" | "OPEN_MARGIN" | "RELEASE_MARGIN" | "ENTRY_FEE" | "EXIT_FEE" | "FUNDING_FEE" | "REALIZED_PNL" | "LIQUIDATION" | "TRANSFER";
  amount: number;
  balance_after: number;
  reference_id?: string;
  description?: string;
}

export interface EquitySnapshot {
  id?: number;
  timestamp: string;
  equity: number;
  wallet: number;
  margin: number;
  unrealized_pnl: number;
  realized_pnl: number;
}

export interface PortfolioState {
  usdt_balance: number;
  available_balance: number;
  margin_used: number;
  total_portfolio_value: number;
  total_unrealized_pnl_usd: number;
  closed_pnl_usd: number;
  daily_pnl_usd: number;
  daily_pnl_pct: number;
  total_pnl_usd: number;
  total_pnl_pct: number;
  win_rate: number;
  total_closed_trades: number;
  auto_bot_enabled: boolean;
  risk_mode: string;
  active_strategy: string;
  active_positions: Position[];
  open_orders?: unknown[];
  trade_history: TradeRecord[];
  pnl_history: EquitySnapshot[];
  ledger: WalletTransaction[];
  accounting_status: "PASS" | "FAIL";
  database_sync_status: string;
  last_validation_time: string;
}


export interface Candle {
  timestamp: number | string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  sma_20?: number;
  ema_9?: number;
}

export interface MarketSummary {
  symbol: string;
  timeframe: string;
  current_price: number;
  rsi: number;
  macd: number;
  vwap: number;
  atr: number;
  trend: string;
  technical_score: number;
  ta_summary: Record<string, number | string>;
  chart_data: Candle[];
}

export interface SubScoreDetail {
  score: number;
  weight: number;
  label: string;
}

export interface ScoreBreakdown {
  ema_trend?: SubScoreDetail;
  macd_momentum?: SubScoreDetail;
  rsi_oscillator?: SubScoreDetail;
  adx_trend_strength?: SubScoreDetail;
  vwap_position?: SubScoreDetail;
  obv_flow?: SubScoreDetail;
  volume_spike?: SubScoreDetail;
  atr_volatility?: SubScoreDetail;
}

export interface AiSignal {
  symbol: string;
  current_price: number;
  action: "STRONG_BUY" | "BUY" | "HOLD" | "SELL" | "STRONG_SELL";
  direction: "LONG" | "SHORT" | "NEUTRAL";
  confidence_score: number;
  composite_score: number;
  technical_score: number;
  sentiment_score: number;
  stop_loss_price: number;
  take_profit_price: number;
  stop_loss_pct: number;
  take_profit_pct: number;
  risk_mode: string;
  strategy: string;
  reasoning: string;
  explainable_reasons?: string[];
  score_breakdown?: ScoreBreakdown;
}


export type ScannerPair = AiSignal;

export interface NewsArticle {
  title: string;
  source: string;
  link: string;
  sentiment: "Bullish" | "Bearish" | "Neutral";
  sentiment_score: number;
  summary?: string;
  published?: string;
  compound?: number;
}

export interface NewsSentiment {
  fear_greed: {
    value: number;
    classification: string;
  };
  sentiment_summary: {
    news_score_avg: number;
    label: string;
  };
  news_articles: NewsArticle[];
}

export interface AccountingAudit {
  wallet: {
    balance: number;
    reconstructed_ledger_balance: number;
    margin_used: number;
  };
  ledger: WalletTransaction[];
  equity: {
    portfolio_value: number;
    unrealized_pnl: number;
    realized_pnl: number;
  };
  positions: Position[];
  trades: TradeRecord[];
  consistency: {
    formula: string;
    mismatch_usdt: number;
    ledger_mismatch: number;
    within_tolerance: boolean;
  };
  audit_status: "PASS" | "FAIL";
  database_sync_status: string;
  last_portfolio_validation: string;
}
