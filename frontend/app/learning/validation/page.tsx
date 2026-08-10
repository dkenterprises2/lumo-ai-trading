"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery } from "@tanstack/react-query";
import { fetchPortfolio, fetchNewsSentiment, toggleBot, setStrategy } from "@/services/api";
import { ShieldCheck, CheckCircle2, AlertTriangle, RefreshCw } from "lucide-react";

export default function ValidationPage() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const stream = useTradingStream();

  const portfolioQuery = useQuery({ queryKey: ["portfolio"], queryFn: fetchPortfolio, refetchInterval: 5000 });
  const newsQuery = useQuery({ queryKey: ["news-sentiment"], queryFn: fetchNewsSentiment, refetchInterval: 300000 });

  const reportQuery = useQuery({
    queryKey: ["performance-report"],
    queryFn: async () => {
      const res = await fetch("/api/learning/performance-report");
      return res.json();
    },
    refetchInterval: 10000
  });

  const currentPortfolio = stream.isConnected && stream.portfolio ? stream.portfolio : portfolioQuery.data ?? null;
  const validations = reportQuery.data?.recent_validations || [];

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500/30">
      <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} connectionState={stream.connectionState} />
      <div className={`flex-1 min-w-0 p-4 transition-all duration-300 lg:p-6 ${sidebarCollapsed ? "ml-20" : "ml-64"}`}>
        <Header portfolio={currentPortfolio} newsSentiment={newsQuery.data ?? null} latency={stream.latency} connectionState={stream.connectionState} onToggleBot={(enable) => toggleBot(enable)} onSelectStrategy={(s) => setStrategy(s)} />

        <main className="space-y-6 max-w-7xl">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
                <ShieldCheck className="w-7 h-7 text-emerald-400" />
                Walk-Forward Backtest Validation Reports
              </h1>
              <p className="text-xs text-slate-400 mt-1">
                Out-of-sample backtest validation guardrails (Sharpe improvement &ge; +0.10, drawdown delta &le; 5%, circuit breaker protection)
              </p>
            </div>
            <button
              onClick={() => reportQuery.refetch()}
              className="bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs px-3 py-2 rounded-xl flex items-center gap-1.5"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${reportQuery.isFetching ? "animate-spin" : ""}`} />
              <span>Refresh Reports</span>
            </button>
          </div>

          {/* Validation Rules Card */}
          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-3">
            <h2 className="text-base font-bold text-white">Backtest Validation Safety Rules</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs font-mono">
              <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
                <div className="text-slate-400">Min Historical Trades</div>
                <div className="text-emerald-400 font-bold text-sm mt-1">&ge; 500 Trades</div>
              </div>
              <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
                <div className="text-slate-400">Sharpe Improvement</div>
                <div className="text-cyan-400 font-bold text-sm mt-1">&ge; +0.10</div>
              </div>
              <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
                <div className="text-slate-400">Max Drawdown Delta</div>
                <div className="text-purple-400 font-bold text-sm mt-1">&le; 5.0%</div>
              </div>
              <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
                <div className="text-slate-400">Circuit Breaker</div>
                <div className="text-amber-400 font-bold text-sm mt-1">&le; 1.25x Drawdown</div>
              </div>
            </div>
          </div>

          {/* Validations List */}
          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4">
            <h2 className="text-base font-bold text-white">Walk-Forward Validation Runs</h2>

            {validations.length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-xs">
                No backtest validation runs recorded yet.
              </div>
            ) : (
              <div className="space-y-4">
                {validations.map((v: any) => (
                  <div key={v.validation_id} className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-sm text-cyan-400">{v.validation_id}</span>
                        <span className="text-xs text-slate-400">({v.experiment_id})</span>
                      </div>
                      {v.approved_for_shadow ? (
                        <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold flex items-center gap-1">
                          <CheckCircle2 className="w-3.5 h-3.5" /> APPROVED FOR SHADOW
                        </span>
                      ) : (
                        <span className="px-2.5 py-0.5 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-bold flex items-center gap-1">
                          <AlertTriangle className="w-3.5 h-3.5" /> REJECTED BY GUARDRAILS
                        </span>
                      )}
                    </div>
                    <pre className="text-xs font-mono text-slate-300 bg-slate-900 p-3 rounded-lg overflow-x-auto whitespace-pre-wrap">
                      {v.validation_report}
                    </pre>
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
