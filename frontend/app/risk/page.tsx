"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery } from "@tanstack/react-query";
import { fetchPortfolio, fetchNewsSentiment, fetchRiskStatus, toggleBot, setStrategy } from "@/services/api";
import { ShieldAlert, ShieldCheck, Activity, Zap, TrendingDown, Layers, Newspaper, RefreshCw } from "lucide-react";

export default function RiskPage() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const stream = useTradingStream();

  const portfolioQuery = useQuery({ queryKey: ["portfolio"], queryFn: fetchPortfolio, refetchInterval: 5000 });
  const newsQuery = useQuery({ queryKey: ["news-sentiment"], queryFn: fetchNewsSentiment, refetchInterval: 300000 });
  const riskStatusQuery = useQuery({ queryKey: ["risk-status"], queryFn: fetchRiskStatus, refetchInterval: 5000 });

  const currentPortfolio = stream.isConnected && stream.portfolio ? stream.portfolio : portfolioQuery.data ?? null;
  const riskStatus = riskStatusQuery.data ?? null;

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500/30">
      <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} connectionState={stream.connectionState} />
      <div className={`flex-1 min-w-0 p-4 transition-all duration-300 lg:p-6 ${sidebarCollapsed ? "ml-20" : "ml-64"}`}>
        <Header portfolio={currentPortfolio} newsSentiment={newsQuery.data ?? null} latency={stream.latency} connectionState={stream.connectionState} onToggleBot={(enable) => toggleBot(enable)} onSelectStrategy={(s) => setStrategy(s)} />
        <main className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                <ShieldAlert className="h-5 w-5" />
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-tight text-slate-100">Institutional Risk Manager & Circuit Breakers</h1>
                <p className="text-xs text-slate-400">10-Rule Pre-Trade Risk Engine & Real-Time Protocol Enforcement</p>
              </div>
            </div>
            {riskStatus && (
              <span className={`px-3 py-1 rounded-xl text-xs font-bold font-mono flex items-center gap-1.5 ${riskStatus.status === "HEALTHY" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30" : "bg-rose-500/10 text-rose-400 border border-rose-500/30"}`}>
                {riskStatus.status === "HEALTHY" ? <ShieldCheck className="h-4 w-4" /> : <ShieldAlert className="h-4 w-4" />}
                SYSTEM {riskStatus.status}
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-1">
              <div className="flex justify-between items-center text-xs text-slate-400">
                <span>Max Daily Loss Limit</span>
                <TrendingDown className="h-4 w-4 text-rose-400" />
              </div>
              <div className="text-lg font-bold text-rose-400 font-mono">
                {riskStatus ? `${riskStatus.daily_pnl_pct}% / -$${riskStatus.config.max_daily_loss_usd}` : "5.0% / -$500.00"}
              </div>
              <p className="text-[11px] text-slate-400">Circuit Breaker Lock on Breach</p>
            </div>

            <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-1">
              <div className="flex justify-between items-center text-xs text-slate-400">
                <span>Peak-to-Trough Drawdown</span>
                <Activity className="h-4 w-4 text-amber-400" />
              </div>
              <div className="text-lg font-bold text-amber-400 font-mono">
                {riskStatus ? `${riskStatus.current_drawdown_pct}% / ${riskStatus.max_drawdown_limit_pct}% Cap` : "0.0% / 10.0% Cap"}
              </div>
              <p className="text-[11px] text-slate-400">Peak Eq: ${riskStatus?.peak_equity_usd ?? "10,000.00"}</p>
            </div>

            <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-1">
              <div className="flex justify-between items-center text-xs text-slate-400">
                <span>Max Concurrent Trades</span>
                <Layers className="h-4 w-4 text-cyan-400" />
              </div>
              <div className="text-lg font-bold text-cyan-400 font-mono">
                {riskStatus ? `${riskStatus.active_concurrent_trades} / ${riskStatus.max_concurrent_trades_limit} Positions` : "0 / 3 Positions"}
              </div>
              <p className="text-[11px] text-slate-400">Strict Slot Limits</p>
            </div>

            <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-1">
              <div className="flex justify-between items-center text-xs text-slate-400">
                <span>Max Exposure Cap</span>
                <Zap className="h-4 w-4 text-purple-400" />
              </div>
              <div className="text-lg font-bold text-purple-400 font-mono">
                {riskStatus ? `${riskStatus.current_exposure_ratio}x / ${riskStatus.max_exposure_ratio_limit}x Cap` : "0.0x / 2.5x Cap"}
              </div>
              <p className="text-[11px] text-slate-400">Total Leverage Notional</p>
            </div>
          </div>

          {/* Institutional Risk Rules Grid */}
          <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl space-y-4">
            <h3 className="font-bold text-slate-100 text-sm">Active Institutional Risk Protections (10 Rules)</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                <span className="font-semibold text-slate-200">1. Correlation Filter</span>
                <p className="text-slate-400">Prevents opening &gt;2 highly correlated altcoins (BTC, ETH, SOL) in the same direction.</p>
              </div>
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                <span className="font-semibold text-slate-200">2. Volatility Filter (ATR Spike)</span>
                <p className="text-slate-400">Blocks new order execution if market ATR volatility exceeds 5.0% of current asset price.</p>
              </div>
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                <span className="font-semibold text-slate-200">3. News Blackout Protocol</span>
                <p className="text-slate-400">Pauses automated trading when Fear &amp; Greed index drops &lt;15 or spikes &gt;85.</p>
              </div>
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                <span className="font-semibold text-slate-200">4. Position Scaling &amp; Risk Per Trade</span>
                <p className="text-slate-400">Scales sizing down 25-50% during drawdown and caps SL loss at 2.0% equity.</p>
              </div>
            </div>
          </div>
        </main>
        <Footer dbSyncStatus={currentPortfolio?.database_sync_status} lastValidationTime={currentPortfolio?.last_validation_time} connectionState={stream.connectionState} />
      </div>
    </div>
  );
}

