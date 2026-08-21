"use client";

import React, { useState } from "react";
import { 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  RotateCw, 
  Clock, 
  Layers, 
  DollarSign, 
  TrendingUp, 
  ExternalLink, 
  Database,
  Cpu
} from "lucide-react";
import { apiFetch } from "@/services/api";

interface ForensicDetailModalProps {
  eventId: string;
  onClose: () => void;
}

export function ArbitrageForensicDetailModal({ eventId, onClose }: ForensicDetailModalProps) {
  const [eventData, setEventData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Replay State
  const [replaying, setReplaying] = useState<boolean>(false);
  const [replayResult, setReplayResult] = useState<any>(null);

  React.useEffect(() => {
    let isMounted = true;
    async function loadDetail() {
      try {
        setLoading(true);
        const res = await apiFetch(`/api/arbitrage/evidence/${eventId}`);
        const data = await res.json();
        if (isMounted) {
          if (data.status === "success" && data.event) {
            setEventData(data.event);
          } else {
            setError(data.message || "Failed to load forensic record");
          }
        }
      } catch (err: any) {
        if (isMounted) setError(err.message || "Network error loading forensic record");
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadDetail();
    return () => { isMounted = false; };
  }, [eventId]);

  const handleReplayDecision = async () => {
    try {
      setReplaying(true);
      const res = await apiFetch(`/api/arbitrage/evidence/${eventId}/replay`, { method: "POST" });
      const data = await res.json();
      setReplayResult(data);
    } catch (err: any) {
      setReplayResult({ status: "error", message: err.message || "Replay execution failed" });
    } finally {
      setReplaying(false);
    }
  };

  const getSourcePublicUrl = (exchange: string, symbol: string) => {
    const s = symbol.replace("/", "").toUpperCase();
    if (exchange === "BINANCE") return `https://www.binance.com/en/trade/${symbol.replace("/", "_")}`;
    if (exchange === "BYBIT") return `https://www.bybit.com/trade/spot/${symbol.replace("/", "")}`;
    if (exchange === "OKX") return `https://www.okx.com/trade-spot/${symbol.toLowerCase().replace("/", "-")}`;
    if (exchange === "KRAKEN") return `https://trade.kraken.com/markets/kraken/${symbol.toLowerCase().replace("/", "")}`;
    if (exchange === "COINBASE") return `https://exchange.coinbase.com/trade/${symbol.replace("/", "-")}`;
    return null;
  };

  return (
    <div className="fixed inset-0 bg-slate-950/85 backdrop-blur-md flex items-center justify-center p-3 sm:p-6 z-50 animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden font-sans">
        
        {/* Header */}
        <div className="px-6 py-4 bg-slate-950/80 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-500/10 border border-indigo-500/30 rounded-xl text-indigo-400">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-white tracking-wide font-mono">
                  Forensic Record: {eventId}
                </h3>
                {eventData?.decision === "EXECUTABLE" ? (
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    EXECUTABLE
                  </span>
                ) : (
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">
                    REJECTED
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400 font-mono">
                {eventData ? `${eventData.symbol} • ${eventData.route_id} • ${eventData.timestamp_utc}` : "Loading event metadata..."}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleReplayDecision}
              disabled={replaying || loading || !eventData}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600/30 hover:bg-indigo-600/50 border border-indigo-500/50 text-indigo-200 text-xs font-mono rounded-lg transition disabled:opacity-50 cursor-pointer"
            >
              <RotateCw className={`w-3.5 h-3.5 ${replaying ? "animate-spin" : ""}`} />
              <span>{replaying ? "Replaying..." : "Replay Decision"}</span>
            </button>
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center transition cursor-pointer text-sm font-bold"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5 custom-scrollbar text-xs">
          {loading ? (
            <div className="py-16 text-center text-slate-400 font-mono flex flex-col items-center gap-2">
              <RotateCw className="w-6 h-6 animate-spin text-indigo-400" />
              <span>Retrieving immutable forensic snapshot from SQLite...</span>
            </div>
          ) : error ? (
            <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 font-mono">
              Error: {error}
            </div>
          ) : !eventData ? (
            <div className="py-16 text-center text-slate-500 font-mono">
              NO REAL RECORDS CAPTURED
            </div>
          ) : (
            <>
              {/* Replay Result Banner */}
              {replayResult && (
                <div className={`p-4 rounded-xl border font-mono ${
                  replayResult.is_match 
                    ? "bg-emerald-950/40 border-emerald-500/40 text-emerald-200" 
                    : "bg-rose-950/40 border-rose-500/40 text-rose-200"
                }`}>
                  <div className="flex items-center justify-between pb-2 border-b border-white/10 mb-2">
                    <div className="flex items-center gap-2 font-bold text-xs">
                      {replayResult.is_match ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <AlertTriangle className="w-4 h-4 text-rose-400" />}
                      <span>Forensic Replay Audit: {replayResult.verification_status}</span>
                    </div>
                    <span className="text-[11px] opacity-75">Deterministic Math Verification</span>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
                    <div>
                      <span className="text-slate-400 block">Original Decision:</span>
                      <strong className={replayResult.original_evaluation.decision === "EXECUTABLE" ? "text-emerald-400" : "text-rose-400"}>
                        {replayResult.original_evaluation.decision} ({replayResult.original_evaluation.rejection_reason})
                      </strong>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Replayed Decision:</span>
                      <strong className={replayResult.replayed_evaluation.decision === "EXECUTABLE" ? "text-emerald-400" : "text-rose-400"}>
                        {replayResult.replayed_evaluation.decision} ({replayResult.replayed_evaluation.rejection_reason})
                      </strong>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Gross Spread:</span>
                      <span>{replayResult.replayed_evaluation.gross_spread_pct?.toFixed(4)}%</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Net Spread:</span>
                      <span className={replayResult.replayed_evaluation.net_edge_pct >= 0 ? "text-emerald-400" : "text-rose-400"}>
                        {replayResult.replayed_evaluation.net_edge_pct?.toFixed(4)}%
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* 1. EVENT METADATA & ROUTE */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
                  <div className="flex items-center gap-1.5 text-indigo-400 font-bold tracking-wide uppercase text-[11px]">
                    <Layers className="w-3.5 h-3.5" />
                    <span>Event Metadata</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 font-mono text-[11px]">
                    <div>
                      <span className="text-slate-400 block">Event ID:</span>
                      <span className="text-slate-200 font-semibold">{eventData.event_id}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Opportunity ID:</span>
                      <span className="text-slate-200">{eventData.opportunity_id || "N/A"}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Scan Cycle ID:</span>
                      <span className="text-slate-300">{eventData.scan_cycle_id || "N/A"}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Execution Status:</span>
                      <span className="text-cyan-400 font-bold">{eventData.execution_status || "REJECTED"}</span>
                    </div>
                    <div className="col-span-2">
                      <span className="text-slate-400 block">UTC Timestamp:</span>
                      <span className="text-slate-300">{eventData.timestamp_utc}</span>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
                  <div className="flex items-center gap-1.5 text-cyan-400 font-bold tracking-wide uppercase text-[11px]">
                    <TrendingUp className="w-3.5 h-3.5" />
                    <span>Route Topology</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 font-mono text-[11px]">
                    <div>
                      <span className="text-slate-400 block">Symbol Pair:</span>
                      <span className="text-white font-bold text-sm">{eventData.symbol}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Route ID:</span>
                      <span className="text-cyan-300 font-semibold">{eventData.route_id}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Buy Exchange:</span>
                      <div className="flex items-center gap-1">
                        <span className="text-emerald-400 font-bold">{eventData.buy_exchange}</span>
                        {getSourcePublicUrl(eventData.buy_exchange, eventData.symbol) && (
                          <a href={getSourcePublicUrl(eventData.buy_exchange, eventData.symbol)!} target="_blank" rel="noreferrer" className="text-slate-400 hover:text-white">
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </div>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Sell Exchange:</span>
                      <div className="flex items-center gap-1">
                        <span className="text-rose-400 font-bold">{eventData.sell_exchange}</span>
                        {getSourcePublicUrl(eventData.sell_exchange, eventData.symbol) && (
                          <a href={getSourcePublicUrl(eventData.sell_exchange, eventData.symbol)!} target="_blank" rel="noreferrer" className="text-slate-400 hover:text-white">
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* 2. ORDERBOOK SIDES (BUY vs SELL) */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Buy Side */}
                <div className="bg-slate-950 p-4 rounded-xl border border-emerald-900/30 space-y-2">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                    <span className="text-emerald-400 font-bold uppercase tracking-wider text-[11px]">
                      Buy Side ({eventData.buy_exchange})
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      Ask Price Used: ${eventData.buy_price_used?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 font-mono text-[11px]">
                    <div>
                      <span className="text-slate-400 block">Best Bid:</span>
                      <span className="text-slate-300">${eventData.buy_bid?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Best Ask:</span>
                      <span className="text-emerald-400 font-bold">${eventData.buy_ask?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Available Depth:</span>
                      <span className="text-slate-200">{eventData.orderbook_depth_buy} {eventData.symbol.split("/")[0]}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Taker Fee:</span>
                      <span className="text-amber-400">{eventData.estimated_fee_buy} bps</span>
                    </div>
                  </div>
                </div>

                {/* Sell Side */}
                <div className="bg-slate-950 p-4 rounded-xl border border-rose-900/30 space-y-2">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                    <span className="text-rose-400 font-bold uppercase tracking-wider text-[11px]">
                      Sell Side ({eventData.sell_exchange})
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      Bid Price Used: ${eventData.sell_price_used?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 font-mono text-[11px]">
                    <div>
                      <span className="text-slate-400 block">Best Bid:</span>
                      <span className="text-rose-400 font-bold">${eventData.sell_bid?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Best Ask:</span>
                      <span className="text-slate-300">${eventData.sell_ask?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Available Depth:</span>
                      <span className="text-slate-200">{eventData.orderbook_depth_sell} {eventData.symbol.split("/")[0]}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Taker Fee:</span>
                      <span className="text-amber-400">{eventData.estimated_fee_sell} bps</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* 3. ECONOMICS & FRICTION BREAKDOWN */}
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3 font-mono">
                <div className="flex items-center gap-1.5 text-amber-400 font-bold uppercase text-[11px]">
                  <DollarSign className="w-3.5 h-3.5" />
                  <span>Economics, Spread &amp; Frictions</span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-[11px]">
                  <div className="p-2.5 bg-slate-900 rounded-lg border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">Gross Spread:</span>
                    <span className={`text-sm font-bold ${eventData.gross_spread_bps > 0 ? "text-cyan-400" : "text-slate-400"}`}>
                      {eventData.gross_spread_bps > 0 ? `+${eventData.gross_spread_bps} bps` : `${eventData.gross_spread_bps} bps`}
                    </span>
                    <span className="text-[10px] text-slate-400 block">({eventData.gross_spread_pct?.toFixed(4)}%)</span>
                  </div>

                  <div className="p-2.5 bg-slate-900 rounded-lg border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">Total Fees (Buy+Sell):</span>
                    <span className="text-sm font-bold text-yellow-400">
                      {(eventData.estimated_fee_buy + eventData.estimated_fee_sell).toFixed(1)} bps
                    </span>
                    <span className="text-[10px] text-slate-400 block">Taker Friction</span>
                  </div>

                  <div className="p-2.5 bg-slate-900 rounded-lg border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">Projected Slippage:</span>
                    <span className="text-sm font-bold text-orange-400">
                      {(eventData.estimated_slippage_buy + eventData.estimated_slippage_sell).toFixed(1)} bps
                    </span>
                    <span className="text-[10px] text-slate-400 block">Depth Impact</span>
                  </div>

                  <div className="p-2.5 bg-slate-900 rounded-lg border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">Net Edge (After All Frictions):</span>
                    <span className={`text-sm font-bold ${eventData.net_edge_bps > 0 ? "text-emerald-400" : "text-rose-400"}`}>
                      {eventData.net_edge_bps > 0 ? `+${eventData.net_edge_bps} bps` : `${eventData.net_edge_bps} bps`}
                    </span>
                    <span className="text-[10px] text-slate-400 block">({eventData.net_edge_pct?.toFixed(4)}%)</span>
                  </div>
                </div>
              </div>

              {/* 4. RISK, GOVERNANCE & FRESHNESS GATES */}
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3 font-mono">
                <div className="flex items-center gap-1.5 text-purple-400 font-bold uppercase text-[11px]">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>Risk, Governance &amp; Latency Gates</span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
                  <div className="p-2 bg-slate-900 rounded border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">Freshness Result:</span>
                    <strong className={eventData.freshness_result === "PASS" ? "text-emerald-400" : "text-amber-400"}>
                      {eventData.freshness_result || "PASS"} ({eventData.quote_age_ms} ms)
                    </strong>
                  </div>
                  <div className="p-2 bg-slate-900 rounded border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">Liquidity Result:</span>
                    <strong className={eventData.liquidity_result === "PASS" ? "text-emerald-400" : "text-indigo-400"}>
                      {eventData.liquidity_result || "PASS"} ({eventData.estimated_quantity} qty)
                    </strong>
                  </div>
                  <div className="p-2 bg-slate-900 rounded border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">Risk Engine Gate:</span>
                    <strong className={eventData.risk_result === "PASS" ? "text-emerald-400" : "text-rose-400"}>
                      {eventData.risk_result || "PASS"}
                    </strong>
                  </div>
                  <div className="p-2 bg-slate-900 rounded border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">Governance Policy:</span>
                    <strong className={eventData.governance_result === "PASS" ? "text-emerald-400" : "text-purple-400"}>
                      {eventData.governance_result || "PASS"}
                    </strong>
                  </div>
                </div>
              </div>

              {/* 5. DATA PROVENANCE & TIMESTAMPS */}
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2 font-mono text-[11px]">
                <div className="flex items-center gap-1.5 text-slate-400 font-bold uppercase text-[10px]">
                  <Cpu className="w-3.5 h-3.5" />
                  <span>Data Provenance &amp; Verification Hashes</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                  <div>
                    <span className="text-slate-500 block">Market Data Source:</span>
                    <span className="text-slate-300">{eventData.market_data_source}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Roundtrip Latency:</span>
                    <span className="text-cyan-400">{eventData.latency_ms} ms</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Final Rejection Reason:</span>
                    <span className="text-amber-300 font-bold">{eventData.rejection_reason}</span>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-slate-950/80 border-t border-slate-800 flex items-center justify-between font-mono text-xs text-slate-400">
          <span>Forensic Evidence Record: {eventId}</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition font-sans text-xs cursor-pointer"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
}
