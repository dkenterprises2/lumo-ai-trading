"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery } from "@tanstack/react-query";
import { fetchPortfolio, fetchNewsSentiment, toggleBot, setStrategy } from "@/services/api";
import { Sliders, RefreshCw, Layers, CheckCircle2, History } from "lucide-react";

export default function ActiveWeightsPage() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const stream = useTradingStream();

  const portfolioQuery = useQuery({ queryKey: ["portfolio"], queryFn: fetchPortfolio, refetchInterval: 5000 });
  const newsQuery = useQuery({ queryKey: ["news-sentiment"], queryFn: fetchNewsSentiment, refetchInterval: 300000 });

  const weightsQuery = useQuery({
    queryKey: ["active-weights"],
    queryFn: async () => {
      const res = await fetch("/api/learning/active-weights?strategy_name=AI_HYBRID&market_regime=NEUTRAL");
      return res.json();
    },
    refetchInterval: 10000
  });

  const currentPortfolio = stream.isConnected && stream.portfolio ? stream.portfolio : portfolioQuery.data ?? null;
  const weightsData = weightsQuery.data;
  const activeWeights = weightsData?.active_weights || {};
  const history = weightsData?.version_history || [];

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500/30">
      <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} connectionState={stream.connectionState} />
      <div className={`flex-1 min-w-0 p-4 transition-all duration-300 lg:p-6 ${sidebarCollapsed ? "ml-20" : "ml-64"}`}>
        <Header portfolio={currentPortfolio} newsSentiment={newsQuery.data ?? null} latency={stream.latency} connectionState={stream.connectionState} onToggleBot={(enable) => toggleBot(enable)} onSelectStrategy={(s) => setStrategy(s)} />

        <main className="space-y-6 max-w-7xl">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
                <Sliders className="w-7 h-7 text-cyan-400" />
                Active Strategy Indicator Weights
              </h1>
              <p className="text-xs text-slate-400 mt-1">
                Dynamic in-memory TTL cached strategy indicator weights (Hot-reloaded every 60 seconds)
              </p>
            </div>
            <button
              onClick={() => weightsQuery.refetch()}
              className="bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs px-3 py-2 rounded-xl flex items-center gap-1.5"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${weightsQuery.isFetching ? "animate-spin" : ""}`} />
              <span>Refresh Weights</span>
            </button>
          </div>

          {/* Active Indicator Weight Visual Progress Bars */}
          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-5">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-cyan-400" />
              Current Active Weights (Strategy: AI_HYBRID | Regime: NEUTRAL)
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {Object.entries(activeWeights).map(([key, val]) => {
                const numVal = typeof val === "number" ? val : 0.1;
                const pct = Math.round(numVal * 100);
                return (
                  <div key={key} className="space-y-1.5">
                    <div className="flex justify-between text-xs font-semibold">
                      <span className="text-slate-300 uppercase tracking-wider">{key.replace("_weight", "").toUpperCase()}</span>
                      <span className="font-mono text-cyan-400">{pct}% (Weight: {numVal.toFixed(4)})</span>
                    </div>
                    <div className="w-full bg-slate-950 h-3 rounded-full overflow-hidden border border-slate-800">
                      <div className="bg-gradient-to-r from-cyan-500 to-indigo-500 h-full rounded-full transition-all duration-500" style={{ width: `${Math.min(pct * 2.5, 100)}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Version History Table */}
          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <History className="w-5 h-5 text-purple-400" />
              Weight Version History Log
            </h2>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
                  <tr>
                    <th className="p-3">Version</th>
                    <th className="p-3">Strategy</th>
                    <th className="p-3">Regime</th>
                    <th className="p-3">Status</th>
                    <th className="p-3">Deployed By</th>
                    <th className="p-3">Timestamp</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {history.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="p-4 text-center text-slate-500">Version 1 (Initial Factory Baseline) Active</td>
                    </tr>
                  ) : (
                    history.map((h: any) => (
                      <tr key={h.version} className="hover:bg-slate-800/40">
                        <td className="p-3 font-bold text-white">v{h.version}</td>
                        <td className="p-3 text-cyan-300">{h.strategy_name}</td>
                        <td className="p-3 text-purple-300">{h.market_regime}</td>
                        <td className="p-3">
                          {h.is_active ? (
                            <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold text-[10px]">ACTIVE</span>
                          ) : (
                            <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 text-[10px]">HISTORICAL</span>
                          )}
                        </td>
                        <td className="p-3 text-slate-300">{h.deployed_by}</td>
                        <td className="p-3 text-slate-400">{h.created_at || "—"}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </main>

        <Footer dbSyncStatus={currentPortfolio?.database_sync_status} lastValidationTime={currentPortfolio?.last_validation_time} connectionState={stream.connectionState} />
      </div>
    </div>
  );
}
