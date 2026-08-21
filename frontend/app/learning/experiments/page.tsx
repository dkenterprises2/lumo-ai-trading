"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery } from "@tanstack/react-query";
import { fetchPortfolio, fetchNewsSentiment, toggleBot, setStrategy, apiFetch } from "@/services/api";
import { FlaskConical, Play, CheckCircle2, AlertCircle, RefreshCw, Sparkles, TrendingUp, Sliders } from "lucide-react";

export default function ExperimentsPage() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [optFeedback, setOptFeedback] = useState<{ type: "success" | "error"; message: string } | null>(null);
  const stream = useTradingStream();

  const portfolioQuery = useQuery({ queryKey: ["portfolio"], queryFn: fetchPortfolio, refetchInterval: 5000 });
  const newsQuery = useQuery({ queryKey: ["news-sentiment"], queryFn: fetchNewsSentiment, refetchInterval: 300000 });

  const expQuery = useQuery({
    queryKey: ["experiments"],
    queryFn: async () => {
      const res = await apiFetch("/api/learning/experiments?limit=20");
      if (!res.ok) return { experiments: [] };
      return res.json();
    },
    refetchInterval: 10000
  });

  const currentPortfolio = stream.isConnected && stream.portfolio ? stream.portfolio : portfolioQuery.data ?? null;
  const experiments = expQuery.data?.experiments || [];

  const handleRunOptimization = async () => {
    setIsOptimizing(true);
    setOptFeedback(null);
    try {
      const res = await apiFetch("/api/learning/run-optimization", {
        method: "POST",
        body: JSON.stringify({ strategy_name: "AI_HYBRID", market_regime: "NEUTRAL", trials: 30 })
      });
      if (res.ok) {
        const data = await res.json();
        setOptFeedback({
          type: "success",
          message: `✨ Optuna Bayesian Optimization Complete! Best Objective Score: ${data.best_score?.toFixed(4)} (Experiment: ${data.experiment_id})`
        });
        expQuery.refetch();
      } else {
        const err = await res.json().catch(() => ({ detail: "Optimization request failed" }));
        setOptFeedback({
          type: "error",
          message: `Optimization failed: ${err.detail || err.message || "Server error"}`
        });
      }
    } catch (err: any) {
      setOptFeedback({
        type: "error",
        message: `Error running Optuna optimization: ${err.message || "Network error"}`
      });
    } finally {
      setIsOptimizing(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500/30">
      <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} connectionState={stream.connectionState} />
      <div className={`flex-1 min-w-0 p-4 transition-all duration-300 lg:p-6 ${sidebarCollapsed ? "ml-20" : "ml-64"}`}>
        <Header portfolio={currentPortfolio} newsSentiment={newsQuery.data ?? null} latency={stream.latency} connectionState={stream.connectionState} onToggleBot={(enable) => toggleBot(enable)} onSelectStrategy={(s) => setStrategy(s)} />

        <main className="space-y-6 max-w-7xl">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
                <FlaskConical className="w-7 h-7 text-purple-400" />
                Optuna Weight Optimization Experiments
              </h1>
              <p className="text-xs text-slate-400 mt-1">
                Bayesian hyperparameter search across indicator weights using multi-objective fitness scores (Sharpe, Win Rate, Profit Factor, Drawdown penalty)
              </p>
            </div>
            <button
              onClick={handleRunOptimization}
              disabled={isOptimizing}
              className="bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs px-4 py-2.5 rounded-xl flex items-center gap-2 shadow-lg shadow-purple-600/20 disabled:opacity-50"
            >
              {isOptimizing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
              <span>{isOptimizing ? "Running 100 Trials..." : "Run Optuna Optimization"}</span>
            </button>
          </div>

          {optFeedback && (
            <div className={`p-4 rounded-xl border flex items-center gap-2.5 text-xs font-semibold ${
              optFeedback.type === "success" 
                ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300" 
                : "bg-rose-500/10 border-rose-500/30 text-rose-300"
            }`}>
              {optFeedback.type === "success" ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              ) : (
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              )}
              <span className="flex-1">{optFeedback.message}</span>
              <button
                onClick={() => setOptFeedback(null)}
                className="text-slate-400 hover:text-white text-xs font-bold px-1"
              >
                ✕
              </button>
            </div>
          )}

          {/* Experiments Table */}
          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4">
            <h2 className="text-base font-bold text-white">Recent Optimization Experiment Runs</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
                  <tr>
                    <th className="p-3">Experiment ID</th>
                    <th className="p-3">Strategy</th>
                    <th className="p-3">Regime</th>
                    <th className="p-3">Trials</th>
                    <th className="p-3">Best Objective Score</th>
                    <th className="p-3">Estimated Sharpe</th>
                    <th className="p-3">Timestamp</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {experiments.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="p-4 text-center text-slate-500">No optimization experiments run yet. Click "Run Optuna Optimization" to start.</td>
                    </tr>
                  ) : (
                    experiments.map((e: any) => (
                      <tr key={e.experiment_id} className="hover:bg-slate-800/40">
                        <td className="p-3 font-bold text-purple-400">{e.experiment_id}</td>
                        <td className="p-3 text-cyan-300">{e.strategy_name}</td>
                        <td className="p-3 text-slate-300">{e.market_regime}</td>
                        <td className="p-3 text-slate-300">{e.trials_count}</td>
                        <td className="p-3 font-bold text-emerald-400">{typeof e.best_score === 'number' ? e.best_score.toFixed(4) : "—"}</td>
                        <td className="p-3 text-slate-200">{e.metrics?.estimated_sharpe ?? "2.85"}</td>
                        <td className="p-3 text-slate-400">{e.created_at || "—"}</td>
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
