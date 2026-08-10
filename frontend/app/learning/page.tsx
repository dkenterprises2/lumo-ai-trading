"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery } from "@tanstack/react-query";
import { fetchPortfolio, fetchNewsSentiment, toggleBot, setStrategy } from "@/services/api";
import { Brain, Sliders, FlaskConical, ShieldCheck, Eye, History, ArrowUpRight, Play, CheckCircle2 } from "lucide-react";

export default function LearningOverviewPage() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const stream = useTradingStream();

  const portfolioQuery = useQuery({ queryKey: ["portfolio"], queryFn: fetchPortfolio, refetchInterval: 5000 });
  const newsQuery = useQuery({ queryKey: ["news-sentiment"], queryFn: fetchNewsSentiment, refetchInterval: 300000 });

  const learningQuery = useQuery({
    queryKey: ["learning-status"],
    queryFn: async () => {
      const res = await fetch("/api/learning/status");
      return res.json();
    },
    refetchInterval: 10000
  });

  const currentPortfolio = stream.isConnected && stream.portfolio ? stream.portfolio : portfolioQuery.data ?? null;
  const learningData = learningQuery.data;

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500/30">
      <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} connectionState={stream.connectionState} />
      <div className={`flex-1 min-w-0 p-4 transition-all duration-300 lg:p-6 ${sidebarCollapsed ? "ml-20" : "ml-64"}`}>
        <Header portfolio={currentPortfolio} newsSentiment={newsQuery.data ?? null} latency={stream.latency} connectionState={stream.connectionState} onToggleBot={(enable) => toggleBot(enable)} onSelectStrategy={(s) => setStrategy(s)} />

        <main className="space-y-6 max-w-7xl">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
                <Brain className="w-7 h-7 text-cyan-400" />
                Self-Learning Feedback Loop &amp; Auto Weight Optimization
              </h1>
              <p className="text-xs text-slate-400 mt-1">
                Continuous reinforcement learning pipeline, Optuna Bayesian hyperparameter optimization, walk-forward validation &amp; shadow governance (v4.1.0-alpha.1)
              </p>
            </div>
          </div>

          {/* Quick Metrics Header Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Learning Status</span>
                <Brain className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-xl font-extrabold text-emerald-400 mt-2 flex items-center gap-1.5">
                <CheckCircle2 className="w-5 h-5" />
                <span>{learningData?.status || "ACTIVE"}</span>
              </div>
              <div className="text-xs text-slate-400 mt-1">Closed-Loop Auto Learning</div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Trade Outcomes Logged</span>
                <History className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="text-2xl font-extrabold text-white mt-2 font-mono">
                {learningData?.total_outcomes_collected ?? 0}
              </div>
              <div className="text-xs text-cyan-400 mt-1">Feature Snapshots: {learningData?.total_snapshots_captured ?? 0}</div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Optimization Trials</span>
                <FlaskConical className="w-4 h-4 text-purple-400" />
              </div>
              <div className="text-2xl font-extrabold text-purple-400 mt-2 font-mono">
                100 Trials / Run
              </div>
              <div className="text-xs text-slate-400 mt-1">Optuna Bayesian Search</div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Governance Guardrails</span>
                <ShieldCheck className="w-4 h-4 text-amber-400" />
              </div>
              <div className="text-xl font-extrabold text-amber-400 mt-2">
                HUMAN APPROVED
              </div>
              <div className="text-xs text-slate-400 mt-1">Multi-Stage Safety Net</div>
            </div>
          </div>

          {/* Module Quick Navigation Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Link href="/learning/weights" className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl hover:border-cyan-500 transition-all group">
              <div className="flex items-center gap-3 text-cyan-400">
                <Sliders className="w-6 h-6" />
                <h3 className="font-bold text-white text-base group-hover:text-cyan-300">Active Indicator Weights</h3>
              </div>
              <p className="text-xs text-slate-400 mt-2">View live strategy indicator weights across EMA, RSI, MACD, ADX, VWAP, OBV and sentiment factors.</p>
            </Link>

            <Link href="/learning/experiments" className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl hover:border-purple-500 transition-all group">
              <div className="flex items-center gap-3 text-purple-400">
                <FlaskConical className="w-6 h-6" />
                <h3 className="font-bold text-white text-base group-hover:text-purple-300">Optuna Weight Experiments</h3>
              </div>
              <p className="text-xs text-slate-400 mt-2">Run Bayesian optimization trials over historical feature snapshots to find higher Sharpe weight sets.</p>
            </Link>

            <Link href="/learning/validation" className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl hover:border-emerald-500 transition-all group">
              <div className="flex items-center gap-3 text-emerald-400">
                <ShieldCheck className="w-6 h-6" />
                <h3 className="font-bold text-white text-base group-hover:text-emerald-300">Walk-Forward Backtest Validation</h3>
              </div>
              <p className="text-xs text-slate-400 mt-2">Verify out-of-sample Sharpe improvement and circuit-breaker drawdown safety thresholds.</p>
            </Link>

            <Link href="/learning/shadow" className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl hover:border-indigo-500 transition-all group">
              <div className="flex items-center gap-3 text-indigo-400">
                <Eye className="w-6 h-6" />
                <h3 className="font-bold text-white text-base group-hover:text-indigo-300">Shadow Evaluation Scorecards</h3>
              </div>
              <p className="text-xs text-slate-400 mt-2">Compare active vs candidate weights in parallel on live market data for 7 consecutive evaluation windows.</p>
            </Link>

            <Link href="/learning/governance" className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl hover:border-amber-500 transition-all group">
              <div className="flex items-center gap-3 text-amber-400">
                <Brain className="w-6 h-6" />
                <h3 className="font-bold text-white text-base group-hover:text-amber-300">Governance &amp; Rollback Manager</h3>
              </div>
              <p className="text-xs text-slate-400 mt-2">Manage production deployment approvals and trigger instant 1-second rollbacks across past weight versions.</p>
            </Link>
          </div>
        </main>

        <Footer dbSyncStatus={currentPortfolio?.database_sync_status} lastValidationTime={currentPortfolio?.last_validation_time} connectionState={stream.connectionState} />
      </div>
    </div>
  );
}
