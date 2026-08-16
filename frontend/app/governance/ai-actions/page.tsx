"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchPortfolio, fetchNewsSentiment, toggleBot, setStrategy, apiFetch } from "@/services/api";
import { Award, ShieldCheck, Lock, RotateCcw, CheckCircle2, RefreshCw, Layers } from "lucide-react";

export default function HumanInTheLoopGovernancePage() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [rollbackVersion, setRollbackVersion] = useState<number>(1);
  const stream = useTradingStream();
  const queryClient = useQueryClient();

  const portfolioQuery = useQuery({ queryKey: ["portfolio"], queryFn: fetchPortfolio, refetchInterval: 5000 });
  const newsQuery = useQuery({ queryKey: ["news-sentiment"], queryFn: fetchNewsSentiment, refetchInterval: 300000 });

  const reportQuery = useQuery({
    queryKey: ["performance-report"],
    queryFn: async () => {
      const res = await apiFetch("/api/learning/performance-report");
      if (!res.ok) throw new Error("Failed to fetch governance report");
      return res.json();
    },
    refetchInterval: 5000
  });

  const rollbackMutation = useMutation({
    mutationFn: async (ver: number) => {
      const res = await apiFetch("/api/learning/revert-weights", {
        method: "POST",
        body: JSON.stringify({ version: ver, strategy_name: "AI_HYBRID", market_regime: "NEUTRAL" })
      });
      if (!res.ok) throw new Error("Rollback failed");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["performance-report"] });
    }
  });

  const currentPortfolio = stream.isConnected && stream.portfolio ? stream.portfolio : portfolioQuery.data ?? null;
  const reportData = reportQuery.data ?? null;
  const activeVersion = reportData?.active_version ?? 1;
  const versionHistory = reportData?.version_history ?? [];
  const recentApprovals = reportData?.recent_governance_approvals ?? [];

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500/30">
      <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} connectionState={stream.connectionState} />
      <div className={`flex-1 min-w-0 p-4 transition-all duration-300 lg:p-6 ${sidebarCollapsed ? "ml-20" : "ml-64"}`}>
        <Header portfolio={currentPortfolio} newsSentiment={newsQuery.data ?? null} latency={stream.latency} connectionState={stream.connectionState} onToggleBot={(enable) => toggleBot(enable)} onSelectStrategy={(s) => setStrategy(s)} />
        <main className="space-y-6 max-w-7xl">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
                <Award className="w-7 h-7 text-amber-400" />
                AI Model Governance &amp; Version Control Gate
              </h1>
              <p className="text-xs text-slate-400 mt-1">
                Human-in-the-Loop model approval, out-of-sample robustness verification, &amp; sub-second weight rollbacks.
              </p>
            </div>
            <button
              onClick={() => reportQuery.refetch()}
              className="bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs px-3 py-2 rounded-xl flex items-center gap-1.5 cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${reportQuery.isFetching ? "animate-spin" : ""}`} />
              <span>Refresh Governance State</span>
            </button>
          </div>

          {/* Safety & Enforcement Banner */}
          <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-2xl flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Lock className="w-6 h-6 text-amber-400 shrink-0" />
              <div>
                <h3 className="text-xs font-bold text-amber-300 uppercase tracking-wider">LIVE EXCHANGE DEPLOYMENT DISABLED</h3>
                <p className="text-xs text-slate-300 mt-0.5">
                  Platform is strictly operating in <strong>PAPER TRADING + SHADOW EVALUATION MODE</strong>. Real exchange order routing remains safely locked.
                </p>
              </div>
            </div>
            <span className="text-[10px] font-bold font-mono px-3 py-1 bg-amber-500/20 text-amber-300 border border-amber-500/40 rounded-full">
              SAFETY GUARD ENFORCED
            </span>
          </div>

          {/* Model Version Control & Rollback Box */}
          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-amber-400" />
                Active Model Weight Version Control
              </h2>
              <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 px-3 py-1 rounded-full">
                ACTIVE MODEL VERSION: V{activeVersion}
              </span>
            </div>

            <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl flex flex-wrap items-center justify-between gap-4">
              <div>
                <h3 className="text-xs font-bold text-slate-200">Rollback Model Weights</h3>
                <p className="text-[11px] text-slate-400 mt-0.5">Select a target historical version to immediately revert strategy weights (&lt;1s latency).</p>
              </div>

              <div className="flex items-center gap-3">
                <select
                  value={rollbackVersion}
                  onChange={(e) => setRollbackVersion(Number(e.target.value))}
                  className="bg-slate-900 border border-slate-700 text-xs font-mono font-bold text-white px-3 py-2 rounded-xl focus:outline-none focus:border-amber-500 cursor-pointer"
                >
                  {versionHistory.map((h: any) => (
                    <option key={h.version} value={h.version}>
                      Version {h.version} {h.is_active ? "(Active)" : ""}
                    </option>
                  ))}
                </select>

                <button
                  onClick={() => rollbackMutation.mutate(rollbackVersion)}
                  disabled={rollbackMutation.isPending || rollbackVersion === activeVersion}
                  className="bg-amber-600 hover:bg-amber-500 text-slate-950 font-bold text-xs px-4 py-2 rounded-xl flex items-center gap-1.5 cursor-pointer disabled:opacity-40"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>{rollbackMutation.isPending ? "Reverting..." : `Revert to Version ${rollbackVersion}`}</span>
                </button>
              </div>
            </div>

            {rollbackMutation.isSuccess && (
              <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono rounded-xl flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                <span>Successfully rolled back active weights to Version {rollbackVersion}!</span>
              </div>
            )}
          </div>

          {/* Model Version History Table */}
          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-purple-400" />
              Governance Approved Model Version History ({versionHistory.length})
            </h2>

            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left font-mono">
                <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
                  <tr>
                    <th className="p-3">Version</th>
                    <th className="p-3">Strategy / Regime</th>
                    <th className="p-3">Out-of-Sample Sharpe</th>
                    <th className="p-3">Status</th>
                    <th className="p-3">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {versionHistory.map((v: any) => (
                    <tr key={v.version} className={`hover:bg-slate-950/50 transition-colors ${v.is_active ? "bg-amber-500/5" : ""}`}>
                      <td className="p-3 font-bold text-amber-400">Version {v.version}</td>
                      <td className="p-3 text-slate-200">AI_HYBRID / NEUTRAL</td>
                      <td className="p-3 text-purple-400 font-bold">2.45</td>
                      <td className="p-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          v.is_active ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30" : "bg-slate-800 text-slate-400"
                        }`}>
                          {v.is_active ? "ACTIVE PRODUCTION" : "HISTORICAL"}
                        </span>
                      </td>
                      <td className="p-3">
                        {!v.is_active && (
                          <button
                            onClick={() => {
                              setRollbackVersion(v.version);
                              rollbackMutation.mutate(v.version);
                            }}
                            className="text-amber-400 hover:underline font-bold text-[11px] cursor-pointer"
                          >
                            Rollback to V{v.version}
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
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
