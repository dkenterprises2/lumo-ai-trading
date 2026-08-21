"use client";

import React, { useState } from "react";
import { X, ShieldAlert, TrendingUp, TrendingDown, RefreshCw, Play, CheckCircle, AlertTriangle, ExternalLink, Activity, DollarSign, Database, Flame, Clock } from "lucide-react";
import { executePaperValidationTest } from "@/services/api";

interface CoinResearchModalProps {
  coinData: any;
  onClose: () => void;
  onRefresh: (symbol: string) => void;
}

export function CoinResearchModal({ coinData, onClose, onRefresh }: CoinResearchModalProps) {
  const [allocation, setAllocation] = useState(250);
  const [isExecuting, setIsExecuting] = useState(false);
  const [tradeResult, setTradeResult] = useState<any>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  if (!coinData || !coinData.coin) return null;

  const { coin, classification, risk_report, dossier } = coinData;

  const handleStartPaperTest = async () => {
    setIsExecuting(true);
    setErrorMessage(null);
    setTradeResult(null);
    try {
      const res = await executePaperValidationTest(coin?.symbol, allocation);
      setTradeResult(res);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to start paper validation test");
    } finally {
      setIsExecuting(false);
    }
  };

  const getRiskColor = (level?: string) => {
    if (level === "HIGH") return "text-rose-400 bg-rose-500/10 border-rose-500/30";
    if (level === "MEDIUM") return "text-amber-400 bg-amber-500/10 border-amber-500/30";
    if (level === "LOW") return "text-emerald-400 bg-emerald-500/10 border-emerald-500/30";
    return "text-gray-400 bg-gray-500/10 border-gray-500/30";
  };

  const getRecBadge = (rec?: string) => {
    if (rec === "PAPER_TEST") return "bg-emerald-500/20 text-emerald-300 border-emerald-500/40";
    if (rec === "WATCH") return "bg-cyan-500/20 text-cyan-300 border-cyan-500/40";
    if (rec === "REJECT") return "bg-rose-500/20 text-rose-300 border-rose-500/40";
    return "bg-gray-500/20 text-gray-300 border-gray-500/40";
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              {classification?.category === "MEME" ? <Flame className="w-6 h-6 text-amber-400" /> : <Activity className="w-6 h-6 text-cyan-400" />}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold text-white tracking-tight">{coin?.symbol}</h2>
                <span className={`px-2.5 py-0.5 text-xs font-semibold rounded-full border ${getRecBadge(dossier?.recommendation)}`}>
                  {dossier?.recommendation || "ANALYZING"}
                </span>
                <span className="px-2 py-0.5 text-xs font-medium rounded-md bg-slate-800 text-slate-300 border border-slate-700">
                  {classification?.category || "UNKNOWN"}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">Venue: <span className="text-slate-200 font-mono">{coin?.exchange}</span> &bull; Source: <span className="text-cyan-400">{coin?.source}</span> &bull; Freshness: <span className="text-emerald-400">{coin?.data_freshness_seconds ?? 0}s ago</span></p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onRefresh(coin?.symbol)}
              className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition border border-slate-700 flex items-center gap-1.5 text-xs font-medium"
              title="Refresh Real-Time Research"
            >
              <RefreshCw className="w-3.5 h-3.5 text-indigo-400" /> Refresh
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition border border-slate-700"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Scrollable Content Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          
          {/* Top Score Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
              <span className="text-[11px] text-slate-400 font-medium block">Current Price</span>
              <span className="text-lg font-bold text-white font-mono mt-1 block">
                ${coin?.current_price !== null && coin?.current_price !== undefined ? (coin.current_price < 0.01 ? coin.current_price.toFixed(6) : coin.current_price.toFixed(2)) : "N/A"}
              </span>
              <span className={`text-xs font-semibold ${(coin?.price_change_24h_pct ?? 0) >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                {(coin?.price_change_24h_pct ?? 0) >= 0 ? "+" : ""}{coin?.price_change_24h_pct?.toFixed(2) ?? "0.00"}% (24h)
              </span>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
              <span className="text-[11px] text-slate-400 font-medium block">AI Opportunity Score</span>
              <span className="text-lg font-bold text-cyan-400 font-mono mt-1 block">{dossier?.opportunity_score ?? 0} / 100</span>
              <span className="text-xs text-slate-400">Multi-factor algorithmic rating</span>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
              <span className="text-[11px] text-slate-400 font-medium block">Overall Risk Score</span>
              <span className={`text-lg font-bold font-mono mt-1 block ${(risk_report?.overall_risk_score ?? 0) > 60 ? "text-rose-400" : "text-emerald-400"}`}>
                {risk_report?.overall_risk_score ?? 0} / 100
              </span>
              <span className={`text-xs font-semibold px-1.5 py-0.2 rounded border ${getRiskColor(risk_report?.overall_risk_level)}`}>
                {risk_report?.overall_risk_level || "UNKNOWN"} RISK
              </span>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
              <span className="text-[11px] text-slate-400 font-medium block">24h Trading Volume</span>
              <span className="text-lg font-bold text-white font-mono mt-1 block">
                {coin?.volume_24h_usd ? `$${(coin.volume_24h_usd / 1e6).toFixed(2)}M` : "N/A"}
              </span>
              <span className="text-xs text-slate-400">Verified venue turnover</span>
            </div>
          </div>

          {/* AI Research Thesis & Catalysts */}
          <div className="p-5 rounded-xl bg-slate-950/60 border border-slate-800 space-y-4">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400">AI Deep Research Synthesis</h3>
              <p className="text-xs text-slate-200 mt-1 leading-relaxed">{dossier?.summary}</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 border-t border-slate-800/80">
              <div>
                <h4 className="text-[11px] font-bold text-emerald-400 flex items-center gap-1.5">
                  <CheckCircle className="w-3.5 h-3.5" /> Bullish Drivers &amp; Momentum Catalysts
                </h4>
                <ul className="mt-2 space-y-1">
                  {(dossier?.bullish_catalysts || []).map((cat: string, i: number) => (
                    <li key={i} className="text-xs text-slate-300 flex items-start gap-1.5">
                      <span className="text-emerald-400">&bull;</span> {cat}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h4 className="text-[11px] font-bold text-rose-400 flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5" /> Bearish Risks &amp; Dilution Overhangs
                </h4>
                <ul className="mt-2 space-y-1">
                  {(dossier?.bearish_risks || []).map((risk: string, i: number) => (
                    <li key={i} className="text-xs text-slate-300 flex items-start gap-1.5">
                      <span className="text-rose-400">&bull;</span> {risk}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* 8-Vector Risk Engine Breakdown */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-amber-400" /> Multi-Vector Risk Engine Evaluation (8 Quantitative Dimensions)
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {(risk_report?.risk_vectors || []).map((vec: any, idx: number) => (
                <div key={idx} className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 flex flex-col justify-between">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">{vec.name}</span>
                    <span className={`px-2 py-0.5 text-[10px] font-bold rounded border ${getRiskColor(vec.level)}`}>
                      {vec.level} ({vec.score}/100)
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-2 leading-snug">{vec.explanation}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Missing Information & Transparency Audit */}
          {(dossier?.missing_information || []).length > 0 && (
            <div className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20 text-xs">
              <span className="font-bold text-amber-400 block mb-1">Data Completeness &amp; Missing Fields Audit:</span>
              <ul className="list-disc list-inside text-slate-300 space-y-0.5">
                {(dossier?.missing_information || []).map((info: string, i: number) => (
                  <li key={i}>{info}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Downstream Gated Paper-Trade Execution Panel */}
          <div className="p-5 rounded-xl bg-gradient-to-br from-indigo-950/40 via-slate-950 to-slate-950 border border-indigo-500/30">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Play className="w-4 h-4 text-emerald-400" /> Gated Paper-Trade Validation Execution
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">Simulate order execution with real orderbook depth, simulated slippage &amp; exchange fees.</p>
              </div>

              <div className="text-right">
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">Decision Gate</span>
                <span className={`px-2.5 py-0.5 rounded text-xs font-bold border ${getRecBadge(dossier?.recommendation)}`}>
                  {dossier?.recommendation}
                </span>
              </div>
            </div>

            {tradeResult ? (
              <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-xs space-y-1">
                <div className="flex items-center gap-2 text-emerald-300 font-bold text-sm">
                  <CheckCircle className="w-4 h-4" /> Paper Validation Trade Executed!
                </div>
                <div className="text-slate-300">
                  Trade ID: <span className="font-mono text-white font-bold">{tradeResult?.trade?.trade_id}</span> &bull; Entry Price: <span className="font-mono text-white font-bold">${Number(tradeResult?.trade?.entry_price || 0).toFixed(6)}</span> &bull; Size: <span className="font-mono text-white font-bold">${tradeResult?.trade?.allocation_usd} USDT</span>
                </div>
                <div className="text-slate-400 text-[11px]">
                  SL: ${Number(tradeResult?.trade?.stop_loss_price || 0).toFixed(6)} (-5%) | TP: ${Number(tradeResult?.trade?.take_profit_price || 0).toFixed(6)} (+15%) | Slippage: ${Number(tradeResult?.trade?.slippage_usd || 0).toFixed(4)}
                </div>
              </div>
            ) : (
              <div className="flex flex-col sm:flex-row items-center gap-3 mt-4">
                <div className="flex items-center gap-2 w-full sm:w-auto">
                  <span className="text-xs text-slate-400 font-medium whitespace-nowrap">Virtual Allocation:</span>
                  <input
                    type="number"
                    value={allocation}
                    onChange={(e) => setAllocation(Number(e.target.value))}
                    min={50}
                    max={2500}
                    step={50}
                    className="w-28 px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs font-mono text-white focus:outline-none focus:border-indigo-500"
                  />
                  <span className="text-xs text-slate-400 font-mono">USDT</span>
                </div>

                <button
                  onClick={handleStartPaperTest}
                  disabled={isExecuting || dossier?.recommendation !== "PAPER_TEST"}
                  className={`w-full sm:w-auto px-5 py-2.5 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition shadow-lg ${
                    dossier?.recommendation === "PAPER_TEST"
                      ? "bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-600/20"
                      : "bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700"
                  }`}
                >
                  <Play className={`w-3.5 h-3.5 ${isExecuting ? "animate-spin" : ""}`} />
                  {isExecuting ? "Executing Validation..." : dossier?.recommendation === "PAPER_TEST" ? "Start Paper Validation Test" : "Blocked by Research Risk Gate"}
                </button>
              </div>
            )}

            {errorMessage && (
              <div className="mt-3 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
                <span>{errorMessage}</span>
              </div>
            )}
          </div>

        </div>

      </div>
    </div>
  );
}
