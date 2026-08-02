"use client";

import React from "react";
import { Activity, BarChart2, Flame } from "lucide-react";
import { MarketSummary, NewsSentiment } from "@/types/trading";

interface RightOrderPanelProps {
  symbol: string;
  marketSummary: MarketSummary | null;
  newsSentiment: NewsSentiment | null;
}

const formatPrice = (value: number | undefined) =>
  value === undefined ? "—" : `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 4 })}`;

export function RightOrderPanel({ symbol, marketSummary, newsSentiment }: RightOrderPanelProps) {
  const fearGreed = newsSentiment?.fear_greed;

  return (
    <div className="space-y-4 rounded-2xl border border-slate-800/80 bg-slate-900/60 p-5 font-mono text-xs shadow-xl backdrop-blur-xl">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-cyan-400" />
          <h3 className="text-sm font-bold text-slate-100">{symbol} Market Data</h3>
        </div>
        <span className={`rounded-lg border px-2.5 py-0.5 text-[10px] font-bold ${
          marketSummary ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400" : "border-slate-700 bg-slate-950 text-slate-500"
        }`}>
          {marketSummary ? "BACKEND LIVE" : "AWAITING DATA"}
        </span>
      </div>

      <div className="space-y-1 rounded-xl border border-slate-800 bg-slate-950 p-3.5 text-center">
        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Current Price</span>
        <div className="text-2xl font-extrabold tracking-tight text-slate-100">{formatPrice(marketSummary?.current_price)}</div>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <Metric label="Trend" value={marketSummary?.trend} accent={marketSummary?.trend === "BULLISH" ? "text-emerald-400" : marketSummary?.trend === "BEARISH" ? "text-rose-400" : "text-slate-200"} />
        <Metric label="Technical score" value={marketSummary ? `${marketSummary.technical_score}/100` : undefined} accent="text-cyan-400" />
        <Metric label="RSI" value={marketSummary?.rsi?.toFixed(2)} accent="text-amber-400" />
        <Metric label="MACD" value={marketSummary?.macd?.toFixed(4)} accent="text-purple-400" />
        <Metric label="VWAP" value={formatPrice(marketSummary?.vwap)} accent="text-slate-200" />
        <Metric label="ATR" value={formatPrice(marketSummary?.atr)} accent="text-slate-200" />
      </div>

      <div className="flex items-center justify-between rounded-xl border border-slate-800/80 bg-slate-950/60 p-2.5">
        <span className="flex items-center gap-1.5 text-slate-400"><Flame className="h-3.5 w-3.5 text-amber-400" /> Fear &amp; Greed</span>
        <span className="font-bold text-amber-400">{fearGreed ? `${fearGreed.value} (${fearGreed.classification})` : "—"}</span>
      </div>

      <p className="flex items-center gap-1.5 text-[10px] text-slate-500"><BarChart2 className="h-3.5 w-3.5" /> Only metrics exposed by the backend are shown.</p>
    </div>
  );
}

function Metric({ label, value, accent }: { label: string; value?: string; accent: string }) {
  return (
    <div className="rounded-xl border border-slate-800/80 bg-slate-950/60 p-2.5">
      <span className="block text-[10px] text-slate-500">{label}</span>
      <span className={`mt-1 block font-bold ${accent}`}>{value ?? "—"}</span>
    </div>
  );
}
