"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery } from "@tanstack/react-query";
import { fetchPortfolio, fetchNewsSentiment, toggleBot, setStrategy, apiFetch } from "@/services/api";
import { Cpu, RefreshCw, Layers, CheckCircle2, ShieldCheck, AlertCircle, Clock, ArrowRight } from "lucide-react";

export default function ExecutionAlgorithmsPage() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const stream = useTradingStream();

  const portfolioQuery = useQuery({ queryKey: ["portfolio"], queryFn: fetchPortfolio, refetchInterval: 5000 });
  const newsQuery = useQuery({ queryKey: ["news-sentiment"], queryFn: fetchNewsSentiment, refetchInterval: 300000 });

  const plannerQuery = useQuery({
    queryKey: ["execution-plans"],
    queryFn: async () => {
      const res = await apiFetch("/api/execution/planner/active-plans");
      if (!res.ok) throw new Error("Failed to fetch execution plans");
      return res.json();
    },
    refetchInterval: 5000
  });

  const currentPortfolio = stream.isConnected && stream.portfolio ? stream.portfolio : portfolioQuery.data ?? null;
  const plans = plannerQuery.data?.plans ?? [];

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500/30">
      <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} connectionState={stream.connectionState} />
      <div className={`flex-1 min-w-0 p-4 transition-all duration-300 lg:p-6 ${sidebarCollapsed ? "ml-20" : "ml-64"}`}>
        <Header portfolio={currentPortfolio} newsSentiment={newsQuery.data ?? null} latency={stream.latency} connectionState={stream.connectionState} onToggleBot={(enable) => toggleBot(enable)} onSelectStrategy={(s) => setStrategy(s)} />
        <main className="space-y-6 max-w-7xl">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
                <Cpu className="w-7 h-7 text-cyan-400" />
                Autonomous Execution Planner &amp; Algorithm Suite
              </h1>
              <p className="text-xs text-slate-400 mt-1">
                Deterministic algorithm selection (DIRECT, TWAP, VWAP, ICEBERG) based on order size, depth utilization, &amp; volatility.
              </p>
            </div>
            <button
              onClick={() => plannerQuery.refetch()}
              className="bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs px-3 py-2 rounded-xl flex items-center gap-1.5 cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${plannerQuery.isFetching ? "animate-spin" : ""}`} />
              <span>Refresh Execution Plans</span>
            </button>
          </div>

          {/* Algorithm Strategy Overview Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl space-y-1.5">
              <span className="font-mono text-xs text-cyan-400 font-bold">DIRECT</span>
              <h3 className="text-sm font-bold text-white">Direct Venue Routing</h3>
              <p className="text-xs text-slate-400">Low-impact small orders or high-urgency multi-leg arbitrage entries.</p>
            </div>

            <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl space-y-1.5">
              <span className="font-mono text-xs text-emerald-400 font-bold">TWAP</span>
              <h3 className="text-sm font-bold text-white">Time-Weighted Slicing</h3>
              <p className="text-xs text-slate-400">Equal interval slicing with randomized jitter for medium-sized orders.</p>
            </div>

            <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl space-y-1.5">
              <span className="font-mono text-xs text-purple-400 font-bold">VWAP</span>
              <h3 className="text-sm font-bold text-white">Volume Profile Slicing</h3>
              <p className="text-xs text-slate-400">U-shaped intraday volume curve distribution for high-volatility orders.</p>
            </div>

            <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl space-y-1.5">
              <span className="font-mono text-xs text-amber-400 font-bold">ICEBERG</span>
              <h3 className="text-sm font-bold text-white">Hidden Reserve Iceberg</h3>
              <p className="text-xs text-slate-400">Hidden quantity reserves for large orders (&gt;20% depth utilization).</p>
            </div>
          </div>

          {/* Active Execution Plans Table */}
          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-cyan-400" />
              Active Autonomous Execution Plans ({plans.length})
            </h2>

            {plans.length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-xs font-mono">
                NO ACTIVE EXECUTION PLANS
              </div>
            ) : (
              <div className="space-y-4">
                {plans.map((p: any) => (
                  <div key={p.plan_id} className="p-5 bg-slate-950 border border-slate-800 rounded-xl space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-sm text-cyan-400">{p.plan_id}</span>
                        <span className="text-xs font-mono text-slate-400">({p.order_id})</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-bold font-mono">
                          {p.selected_algorithm}
                        </span>
                        <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold font-mono ${
                          p.execution_mode === "PAPER" || p.execution_mode === "SHADOW"
                            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                            : "bg-rose-500/10 text-rose-400 border border-rose-500/30"
                        }`}>
                          {p.execution_mode} MODE
                        </span>
                      </div>
                    </div>

                    <p className="text-xs font-mono text-slate-300 bg-slate-900 p-3 rounded-lg border border-slate-800">
                      {p.reason}
                    </p>

                    <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-xs font-mono">
                      <div className="p-2.5 bg-slate-900 rounded-lg">
                        <div className="text-slate-400">Symbol &amp; Side</div>
                        <div className="text-white font-bold mt-0.5">{p.symbol} ({p.side})</div>
                      </div>
                      <div className="p-2.5 bg-slate-900 rounded-lg">
                        <div className="text-slate-400">Quantity</div>
                        <div className="text-white font-bold mt-0.5">{p.quantity}</div>
                      </div>
                      <div className="p-2.5 bg-slate-900 rounded-lg">
                        <div className="text-slate-400">Duration &amp; Slices</div>
                        <div className="text-purple-400 font-bold mt-0.5">{p.duration_seconds}s ({p.slice_count} Slices)</div>
                      </div>
                      <div className="p-2.5 bg-slate-900 rounded-lg">
                        <div className="text-slate-400">Expected Slippage</div>
                        <div className="text-emerald-400 font-bold mt-0.5">{p.expected_slippage_bps} bps</div>
                      </div>
                      <div className="p-2.5 bg-slate-900 rounded-lg">
                        <div className="text-slate-400">Urgency</div>
                        <div className="text-amber-400 font-bold mt-0.5">{p.urgency}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </main>
        <Footer dbSyncStatus={currentPortfolio?.database_sync_status} lastValidationTime={currentPortfolio?.last_validation_time} connectionState={stream.connectionState} />
      </div>
    </div>
  );
}
