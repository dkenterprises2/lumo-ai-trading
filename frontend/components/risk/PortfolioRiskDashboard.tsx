"use client";

import React, { useState, useEffect } from "react";
import { 
  ShieldAlert, 
  Activity, 
  TrendingDown, 
  Layers, 
  Flame, 
  PieChart, 
  Zap, 
  AlertTriangle, 
  CheckCircle2, 
  Power,
  RefreshCw
} from "lucide-react";
import { apiFetch } from "@/services/api";

interface RiskState {
  equity: number;
  available_balance: number;
  unrealized_pnl: number;
  drawdown_pct: number;
  volatility_regime: string;
  market_regime: string;
  open_positions: number;
  configured_max_positions: number;
  dynamic_max_positions: number;
  effective_max_positions: number;
  portfolio_heat_pct: number;
  correlation_risk_score: number;
  concentration_risk_score: number;
  risk_budget_remaining_pct: number;
  risk_score: number;
  overall_status: string;
  metadata?: any;
}

export default function PortfolioRiskDashboard() {
  const [riskData, setRiskData] = useState<RiskState | null>(null);
  const [killSwitch, setKillSwitch] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [explainability, setExplainability] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchRiskMetrics = async () => {
    try {
      const [resPortfolio, resKs, resRecs, resExp] = await Promise.all([
        apiFetch("/api/risk/portfolio"),
        apiFetch("/api/risk/kill-switch"),
        apiFetch("/api/risk/recommendations"),
        apiFetch("/api/risk/explainability")
      ]);

      if (resPortfolio.ok) setRiskData(await resPortfolio.json());
      if (resKs.ok) setKillSwitch(await resKs.json());
      if (resRecs.ok) setRecommendations(await resRecs.json());
      if (resExp.ok) setExplainability(await resExp.json());
    } catch (e) {
      console.error("Failed to fetch risk dashboard data", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRiskMetrics();
    const interval = setInterval(fetchRiskMetrics, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleToggleKillSwitch = async (action: "activate" | "recover") => {
    try {
      const res = await apiFetch(`/api/risk/kill-switch/${action}`, {
        method: "POST",
        body: JSON.stringify({ reason: `User manual ${action} from dashboard` })
      });
      if (res.ok) {
        fetchRiskMetrics();
      }
    } catch (e) {
      console.error(`Failed to ${action} kill switch`, e);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12 text-slate-400">
        <RefreshCw className="w-6 h-6 animate-spin mr-2" />
        <span>Loading Institutional Portfolio Risk Intelligence...</span>
      </div>
    );
  }

  const tradeLimit = riskData?.metadata?.trade_limit || {};
  const isHalted = killSwitch?.state === "HALTED" || riskData?.overall_status === "HALTED";

  const configuredMax = (riskData?.configured_max_positions && riskData.configured_max_positions > 0) ? riskData.configured_max_positions : (tradeLimit?.configured_max_positions || 10);
  const dynamicMax = (riskData?.dynamic_max_positions && riskData.dynamic_max_positions > 0) ? riskData.dynamic_max_positions : (tradeLimit?.dynamic_risk_limit || 10);
  const effectiveMax = isHalted ? 0 : ((riskData?.effective_max_positions && riskData.effective_max_positions > 0) ? riskData.effective_max_positions : (tradeLimit?.effective_max_positions || 10));
  const openPositions = riskData?.open_positions ?? 0;
  const availableSlots = isHalted ? 0 : (tradeLimit?.available_trade_slots ?? Math.max(0, effectiveMax - openPositions));
  const hasPositions = openPositions > 0;
  const scoreVal = riskData?.risk_score;

  return (
    <div className="space-y-6 text-slate-100 font-sans">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between bg-slate-900/80 border border-slate-800 p-6 rounded-2xl backdrop-blur-md">
        <div>
          <div className="flex items-center space-x-3">
            <ShieldAlert className="w-8 h-8 text-cyan-400" />
            <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
              Institutional Risk Engine 2.0 (Phase 34)
            </h1>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Dynamic correlation control, drawdown adaptation, portfolio heat metrics, and automated circuit breakers.
          </p>
        </div>

        {/* Kill Switch Controls */}
        <div className="mt-4 md:mt-0 flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <span className="text-xs text-slate-400 uppercase font-semibold">Kill-Switch:</span>
            <span className={`px-2.5 py-1 rounded-full text-xs font-mono font-bold ${isHalted ? "bg-rose-500/20 text-rose-400 border border-rose-500/30 animate-pulse" : "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"}`}>
              {killSwitch?.state || "NORMAL"}
            </span>
          </div>

          {isHalted ? (
            <button
              onClick={() => handleToggleKillSwitch("recover")}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-sm rounded-xl transition-all shadow-lg shadow-emerald-900/30 flex items-center space-x-2"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Authorize Recovery</span>
            </button>
          ) : (
            <button
              onClick={() => handleToggleKillSwitch("activate")}
              className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white font-medium text-sm rounded-xl transition-all shadow-lg shadow-rose-900/30 flex items-center space-x-2"
            >
              <Power className="w-4 h-4" />
              <span>Halt All Entries</span>
            </button>
          )}
        </div>
      </div>

      {/* Top 4 Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Risk Score Card */}
        <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl backdrop-blur-md">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Portfolio Risk Score</span>
            <Activity className="w-5 h-5 text-cyan-400" />
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            {hasPositions && scoreVal !== null && scoreVal !== undefined ? (
              <>
                <span className="text-3xl font-mono font-bold text-slate-100">{scoreVal}</span>
                <span className="text-xs text-slate-400">/ 100</span>
              </>
            ) : (
              <div>
                <span className="text-3xl font-mono font-bold text-slate-400">N/A</span>
                <span className="ml-2 text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700 font-sans">
                  No active positions
                </span>
              </div>
            )}
          </div>
          <div className="w-full bg-slate-800 h-2 rounded-full mt-3 overflow-hidden">
            <div 
              className={`h-full transition-all duration-500 ${
                !hasPositions ? "bg-slate-600" : (scoreVal || 0) > 70 ? "bg-rose-500" : (scoreVal || 0) > 40 ? "bg-amber-500" : "bg-cyan-500"
              }`}
              style={{ width: `${hasPositions ? Math.min(100, scoreVal || 0) : 0}%` }}
            />
          </div>
        </div>

        {/* Portfolio Heat Card */}
        <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl backdrop-blur-md">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Portfolio Heat</span>
            <Flame className="w-5 h-5 text-amber-400" />
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-mono font-bold text-amber-400">{riskData?.portfolio_heat_pct ?? 0}%</span>
            <span className="text-xs text-slate-400">Net Risk</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Budget Utilization: <span className="font-mono text-slate-200">{riskData?.metadata?.heat?.utilization_pct || 0}%</span>
          </p>
        </div>

        {/* Drawdown Meter Card */}
        <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl backdrop-blur-md">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Current Drawdown</span>
            <TrendingDown className="w-5 h-5 text-rose-400" />
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-mono font-bold text-rose-400">{riskData?.drawdown_pct ?? 0}%</span>
            <span className="text-xs text-slate-400">Peak-to-Trough</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Status: <span className="font-mono text-slate-200">{riskData?.metadata?.drawdown?.trading_status || "NORMAL"}</span>
          </p>
        </div>

        {/* Dynamic Effective Limit Card */}
        <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl backdrop-blur-md">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Dynamic Safe Limit</span>
            <Layers className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-mono font-bold text-emerald-400">{effectiveMax}</span>
            <span className="text-xs text-slate-400">/ {configuredMax} Max</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Available Slots: <span className="font-mono text-emerald-300 font-bold">{availableSlots}</span>
          </p>
        </div>
      </div>

      {/* Dynamic Trade Limit Details & Trade Block Explanation */}
      <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl backdrop-blur-md space-y-4">
        <div className="flex items-center space-x-2">
          <Zap className="w-5 h-5 text-cyan-400" />
          <h2 className="text-lg font-bold text-slate-200">Dynamic Effective Trade Limit breakdown</h2>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-slate-950/60 p-4 rounded-xl border border-slate-800/80 font-mono text-sm">
          <div>
            <div className="text-xs text-slate-400 font-sans">User Hard Ceiling</div>
            <div className="text-lg font-bold text-slate-200">{configuredMax} Trades</div>
          </div>
          <div>
            <div className="text-xs text-slate-400 font-sans">Dynamic Risk Limit</div>
            <div className="text-lg font-bold text-cyan-400">{dynamicMax} Trades</div>
          </div>
          <div>
            <div className="text-xs text-slate-400 font-sans">Currently Open</div>
            <div className="text-lg font-bold text-amber-400">{openPositions} Trades</div>
          </div>
          <div>
            <div className="text-xs text-slate-400 font-sans">Available Open Slots</div>
            <div className="text-lg font-bold text-emerald-400">{availableSlots} Slots</div>
          </div>
        </div>

        {availableSlots === 0 && (

          <div className="flex items-start space-x-3 bg-amber-500/10 border border-amber-500/30 p-4 rounded-xl text-amber-300 text-sm">
            <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold">Why the bot cannot open another trade:</span>
              <p className="mt-1 text-slate-300">
                The Dynamic Risk Engine set a safe maximum limit of <span className="font-mono text-cyan-300 font-bold">{riskData?.effective_max_positions}</span> trades (constrained by <span className="font-mono text-amber-300 font-bold">{tradeLimit?.constraining_factor || "RISK_BUDGET"}</span>). You currently have {riskData?.open_positions} open positions.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Risk Score Explainability: Why is my risk score X? */}
      <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl backdrop-blur-md space-y-4">
        <div className="flex items-center space-x-2">
          <Activity className="w-5 h-5 text-cyan-400" />
          <h2 className="text-lg font-bold text-slate-200">Why is my risk score {hasPositions && scoreVal !== null && scoreVal !== undefined ? scoreVal : "N/A"}?</h2>
        </div>

        <p className="text-xs text-slate-400">
          {explainability?.risk_drivers?.explanation || "Risk score is calculated deterministically from active position heat, correlation, concentration, drawdown, volatility, budget, and leverage factors."}
        </p>

        {explainability?.risk_drivers?.factors ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            {Object.entries(explainability.risk_drivers.factors).map(([fKey, fVal]: [string, any]) => (
              <div key={fKey} className="bg-slate-950/60 p-3 rounded-xl border border-slate-800 space-y-1 font-mono text-xs">
                <div className="text-slate-400 font-sans uppercase text-[10px] tracking-wider font-bold">
                  {fKey.replace('_', ' ')} (Weight: {(fVal.weight * 100).toFixed(0)}%)
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-slate-300 font-bold">Score: {fVal.score}</span>
                  <span className="text-cyan-400 font-bold">+{fVal.contribution} pts</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-xs text-slate-500 bg-slate-950/40 p-3 rounded-xl border border-slate-850">
            Open positions to see live factor contributions to your portfolio risk score.
          </div>
        )}
      </div>

      {/* AI Risk Advisory & Recommendations */}
      <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl backdrop-blur-md space-y-4">
        <h2 className="text-lg font-bold text-slate-200 flex items-center space-x-2">
          <PieChart className="w-5 h-5 text-indigo-400" />
          <span>Structured AI Risk Recommendations</span>
        </h2>

        {recommendations.length === 0 ? (
          <div className="text-slate-400 text-sm bg-slate-950/40 p-4 rounded-xl border border-slate-800">
            No active risk warnings or concentration hazards detected. Portfolio risk structure is healthy.
          </div>
        ) : (
          <div className="space-y-3">
            {recommendations.map((rec, idx) => (
              <div key={idx} className="bg-slate-950/60 border border-slate-800 p-4 rounded-xl flex items-start justify-between">
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-0.5 text-xs font-mono font-bold rounded ${rec.severity === "HIGH" ? "bg-rose-500/20 text-rose-400" : "bg-amber-500/20 text-amber-400"}`}>
                      {rec.severity}
                    </span>
                    <span className="text-sm font-semibold text-slate-200">{rec.recommendation}</span>
                  </div>
                  <div className="text-xs text-slate-400">
                    Affected Symbols: <span className="font-mono text-cyan-300">{rec.affected_symbols.join(", ") || "PORTFOLIO"}</span>
                  </div>
                </div>
                <div className="text-right font-mono text-xs text-slate-400">
                  Confidence: <span className="text-emerald-400 font-bold">{(rec.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
