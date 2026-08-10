"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery } from "@tanstack/react-query";
import { fetchPortfolio, fetchNewsSentiment, toggleBot, setStrategy } from "@/services/api";
import { Brain, ShieldCheck, RotateCcw, CheckCircle2, RefreshCw, AlertTriangle } from "lucide-react";

export default function GovernancePage() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [rollbackVersion, setRollbackVersion] = useState<string>("1");
  const [actionFeedback, setActionFeedback] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

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

  const weightsQuery = useQuery({
    queryKey: ["active-weights"],
    queryFn: async () => {
      const res = await fetch("/api/learning/active-weights?strategy_name=AI_HYBRID&market_regime=NEUTRAL");
      return res.json();
    },
    refetchInterval: 10000
  });

  const currentPortfolio = stream.isConnected && stream.portfolio ? stream.portfolio : portfolioQuery.data ?? null;
  const approvals = reportQuery.data?.recent_governance_approvals || [];
  const versionHistory = weightsQuery.data?.version_history || [];

  const handleRollback = async () => {
    const ver = parseInt(rollbackVersion, 10);
    if (isNaN(ver) || ver < 1) return;

    setIsProcessing(true);
    setActionFeedback(null);
    try {
      const res = await fetch("/api/learning/revert-weights", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ version: ver, strategy_name: "AI_HYBRID", market_regime: "NEUTRAL" })
      });
      const data = await res.json();
      setActionFeedback(`Instant 1-second Rollback Successful! Active weights restored to Version ${ver}.`);
      weightsQuery.refetch();
      reportQuery.refetch();
    } catch (err: any) {
      setActionFeedback(`Rollback error: ${err.message}`);
    } finally {
      setIsProcessing(false);
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
                <Brain className="w-7 h-7 text-amber-400" />
                Governance Approvals &amp; Instant Rollback Manager
              </h1>
              <p className="text-xs text-slate-400 mt-1">
                Multi-stage deployment governance (DRAFT → UNDER_REVIEW → SHADOW_APPROVED → PRODUCTION_APPROVED) &amp; 1-second instant rollbacks
              </p>
            </div>
          </div>

          {actionFeedback && (
            <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-semibold flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-amber-400 flex-shrink-0" />
              <span>{actionFeedback}</span>
            </div>
          )}

          {/* Instant 1-Second Rollback Control Card */}
          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <RotateCcw className="w-5 h-5 text-amber-400" />
              Instant 1-Second Weight Version Rollback
            </h2>
            <p className="text-xs text-slate-400">
              Select any of the last 10 historical weight versions to trigger an emergency hot rollback in under 1.0 second.
            </p>

            <div className="flex flex-wrap items-center gap-3">
              <select
                value={rollbackVersion}
                onChange={(e) => setRollbackVersion(e.target.value)}
                className="bg-slate-950 border border-slate-800 text-white font-mono text-xs px-4 py-2.5 rounded-xl focus:outline-none focus:border-amber-500"
              >
                {versionHistory.length === 0 ? (
                  <option value="1">Version 1 (Initial Factory Baseline)</option>
                ) : (
                  versionHistory.map((h: any) => (
                    <option key={h.version} value={h.version}>
                      Version {h.version} — Deployed by {h.deployed_by} ({h.is_active ? "ACTIVE" : "HISTORICAL"})
                    </option>
                  ))
                )}
              </select>

              <button
                onClick={handleRollback}
                disabled={isProcessing}
                className="bg-amber-600 hover:bg-amber-500 text-slate-950 font-bold text-xs px-4 py-2.5 rounded-xl flex items-center gap-2 transition-all shadow-lg shadow-amber-600/20 disabled:opacity-50"
              >
                {isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <RotateCcw className="w-4 h-4" />}
                <span>Trigger Instant Rollback</span>
              </button>
            </div>
          </div>

          {/* Governance Approvals Audit Log */}
          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
              Governance Production Deployment Audit Log
            </h2>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
                  <tr>
                    <th className="p-3">Approval ID</th>
                    <th className="p-3">Experiment ID</th>
                    <th className="p-3">Governance Status</th>
                    <th className="p-3">Human Approved</th>
                    <th className="p-3">Approved By</th>
                    <th className="p-3">Deployed Timestamp</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {approvals.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="p-4 text-center text-slate-500">Initial Factory Baseline Version 1 Active. No custom deployments yet.</td>
                    </tr>
                  ) : (
                    approvals.map((a: any) => (
                      <tr key={a.approval_id} className="hover:bg-slate-800/40">
                        <td className="p-3 font-bold text-amber-400">{a.approval_id}</td>
                        <td className="p-3 text-cyan-300">{a.experiment_id}</td>
                        <td className="p-3">
                          <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold text-[10px]">
                            {a.status}
                          </span>
                        </td>
                        <td className="p-3 text-slate-200">{a.human_approval ? "TRUE (Explicit)" : "FALSE"}</td>
                        <td className="p-3 text-slate-300">{a.approved_by || "admin@lumo.trade"}</td>
                        <td className="p-3 text-slate-400">{a.deployed_at || a.created_at}</td>
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
