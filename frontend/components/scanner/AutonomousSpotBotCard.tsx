"use client";

import React, { useState, useEffect } from "react";
import { 
  Bot, ShieldAlert, TrendingUp, TrendingDown, RefreshCw, Play, Pause, 
  Settings, DollarSign, Wallet, Brain, Sparkles, AlertTriangle, 
  CheckCircle, ArrowUpRight, ArrowDownRight, Activity, X, RotateCcw,
  Sliders, Layers
} from "lucide-react";
import { 
  fetchSpotBotStatus, updateSpotBotConfig, toggleSpotBot, 
  resetSpotSubWallet, closeSpotBotTrade 
} from "@/services/api";

export function AutonomousSpotBotCard() {
  const [statusData, setStatusData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [showLessonsModal, setShowLessonsModal] = useState(false);
  const [feedbackMsg, setFeedbackMsg] = useState<string | null>(null);

  // Form State for User Parameters
  const [capitalPerTrade, setCapitalPerTrade] = useState<number>(250);
  const [maxPositions, setMaxPositions] = useState<number>(5);
  const [minOppScore, setMinOppScore] = useState<number>(65);
  const [maxRiskScore, setMaxRiskScore] = useState<number>(50);
  const [tpPct, setTpPct] = useState<number>(12);
  const [slPct, setSlPct] = useState<number>(5);
  const [autoLearn, setAutoLearn] = useState<boolean>(true);

  const loadBotStatus = async () => {
    try {
      const data = await fetchSpotBotStatus();
      setStatusData(data);
      if (data?.config) {
        setCapitalPerTrade(data.config.allocation_per_trade_usd ?? 250);
        setMaxPositions(data.config.max_active_positions ?? 5);
        setMinOppScore(data.config.min_opportunity_score ?? 65);
        setMaxRiskScore(data.config.max_risk_score ?? 50);
        setTpPct(data.config.take_profit_pct ?? 12);
        setSlPct(data.config.stop_loss_pct ?? 5);
        setAutoLearn(data.config.auto_learn_enabled ?? true);
      }
    } catch (err) {
      console.error("Failed to load spot bot status:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBotStatus();
    const interval = setInterval(loadBotStatus, 4000); // 4s polling for live ticking PnL
    return () => clearInterval(interval);
  }, []);

  const handleToggleBot = async () => {
    setUpdating(true);
    try {
      await toggleSpotBot();
      await loadBotStatus();
      setFeedbackMsg("Bot status toggled successfully!");
      setTimeout(() => setFeedbackMsg(null), 3000);
    } catch (err: any) {
      setFeedbackMsg(`Error: ${err.message}`);
    } finally {
      setUpdating(false);
    }
  };

  const handleSaveConfig = async (e: React.FormEvent) => {
    e.preventDefault();
    setUpdating(true);
    try {
      const payload = {
        is_enabled: statusData?.config?.is_enabled ?? true,
        allocation_per_trade_usd: Number(capitalPerTrade),
        max_active_positions: Number(maxPositions),
        min_opportunity_score: Number(minOppScore),
        max_risk_score: Number(maxRiskScore),
        take_profit_pct: Number(tpPct),
        stop_loss_pct: Number(slPct),
        scan_interval_seconds: 20,
        allowed_categories: ["MEME", "NEW", "ESTABLISHED"],
        auto_learn_enabled: autoLearn
      };
      await updateSpotBotConfig(payload);
      await loadBotStatus();
      setShowConfigModal(false);
      setFeedbackMsg("Parameters updated successfully!");
      setTimeout(() => setFeedbackMsg(null), 3000);
    } catch (err: any) {
      setFeedbackMsg(`Error updating config: ${err.message}`);
    } finally {
      setUpdating(false);
    }
  };

  const handleResetWallet = async () => {
    if (!confirm("Are you sure you want to reset the isolated Spot Sub-Wallet to $10,000.00 USDT?")) return;
    setUpdating(true);
    try {
      await resetSpotSubWallet(10000);
      await loadBotStatus();
      setFeedbackMsg("Spot Sub-Wallet reset to $10,000.00 USDT!");
      setTimeout(() => setFeedbackMsg(null), 3000);
    } catch (err: any) {
      setFeedbackMsg(`Error resetting wallet: ${err.message}`);
    } finally {
      setUpdating(false);
    }
  };

  const handleCloseTrade = async (tradeId: string) => {
    try {
      await closeSpotBotTrade(tradeId);
      await loadBotStatus();
    } catch (err: any) {
      alert(`Failed to close trade: ${err.message}`);
    }
  };

  const isRunning = statusData?.is_running ?? false;
  const wallet = statusData?.wallet ?? {};
  const activePositions = statusData?.active_positions ?? [];
  const lessons = statusData?.learned_lessons ?? [];

  return (
    <div className="mb-8 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900/90 to-indigo-950/40 border border-indigo-500/30 p-6 shadow-2xl backdrop-blur-md">
      
      {/* Top Banner: Bot Title & Controls */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        
        {/* Title & Status Indicator */}
        <div className="flex items-center gap-4">
          <div className="relative p-3 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 shadow-inner">
            <Bot className="w-8 h-8 animate-pulse text-indigo-400" />
            <span className={`absolute top-1 right-1 w-3 h-3 rounded-full ${isRunning ? "bg-emerald-400 shadow-[0_0_8px_#34d399]" : "bg-amber-400"}`} />
          </div>
          
          <div>
            <div className="flex items-center gap-2.5">
              <h2 className="text-xl font-bold text-white tracking-tight">Autonomous Spot &amp; Meme Coin Learner Bot</h2>
              <span className={`px-2.5 py-0.5 text-xs font-bold rounded-full border ${
                isRunning 
                  ? "bg-emerald-500/15 text-emerald-300 border-emerald-500/30" 
                  : "bg-amber-500/15 text-amber-300 border-amber-500/30"
              }`}>
                {isRunning ? "● ACTIVE SCANNING" : "⏸ PAUSED"}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Autonomous paper validation with isolated sub-wallet &bull; Continuous reinforcement self-learning loop.
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center flex-wrap gap-2.5">
          {feedbackMsg && (
            <span className="text-xs text-emerald-400 font-medium bg-emerald-500/10 border border-emerald-500/20 px-3 py-1.5 rounded-xl">
              {feedbackMsg}
            </span>
          )}

          <button
            onClick={handleToggleBot}
            disabled={updating}
            className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition shadow-lg ${
              isRunning
                ? "bg-amber-600/20 text-amber-300 hover:bg-amber-600/30 border border-amber-500/40"
                : "bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-600/20"
            }`}
          >
            {isRunning ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            {isRunning ? "Pause Bot" : "Start Autonomous Bot"}
          </button>

          <button
            onClick={() => setShowConfigModal(true)}
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold flex items-center gap-1.5 border border-slate-700 transition"
          >
            <Sliders className="w-4 h-4 text-indigo-400" />
            Parameters
          </button>

          <button
            onClick={() => setShowLessonsModal(true)}
            className="px-3.5 py-2 rounded-xl bg-indigo-500/15 hover:bg-indigo-500/25 text-indigo-300 text-xs font-bold flex items-center gap-1.5 border border-indigo-500/30 transition"
          >
            <Brain className="w-4 h-4 text-cyan-400" />
            Learned Lessons ({statusData?.learned_lessons_count ?? 0})
          </button>

          <button
            onClick={handleResetWallet}
            className="p-2 rounded-xl bg-slate-800/80 hover:bg-rose-500/20 hover:text-rose-300 text-slate-400 text-xs border border-slate-700 transition"
            title="Reset Sub-Wallet to $10,000 USDT"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Metric Cards Grid: Sub-Wallet & Performance */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 pt-6">
        
        {/* 1. Available USDT in Sub-Wallet */}
        <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-[11px] font-medium">
            <span>Spot Sub-Wallet</span>
            <Wallet className="w-3.5 h-3.5 text-indigo-400" />
          </div>
          <div className="mt-1">
            <span className="text-lg font-bold text-white font-mono block">
              ${(wallet.usdt_available_balance ?? 10000).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
            <span className="text-[10px] text-slate-400 font-mono">Available Virtual USDT</span>
          </div>
        </div>

        {/* 2. Total Equity */}
        <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-[11px] font-medium">
            <span>Total Equity</span>
            <DollarSign className="w-3.5 h-3.5 text-cyan-400" />
          </div>
          <div className="mt-1">
            <span className="text-lg font-bold text-cyan-300 font-mono block">
              ${(wallet.total_equity_usd ?? 10000).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
            <span className={`text-[10px] font-semibold ${(wallet.roi_total_pct ?? 0) >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
              {(wallet.roi_total_pct ?? 0) >= 0 ? "+" : ""}{wallet.roi_total_pct ?? 0}% Total ROI
            </span>
          </div>
        </div>

        {/* 3. Realized PnL */}
        <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-[11px] font-medium">
            <span>Realized PnL</span>
            {(wallet.realized_pnl_usd ?? 0) >= 0 ? <ArrowUpRight className="w-3.5 h-3.5 text-emerald-400" /> : <ArrowDownRight className="w-3.5 h-3.5 text-rose-400" />}
          </div>
          <div className="mt-1">
            <span className={`text-lg font-bold font-mono block ${(wallet.realized_pnl_usd ?? 0) >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
              {(wallet.realized_pnl_usd ?? 0) >= 0 ? "+" : ""}${(wallet.realized_pnl_usd ?? 0).toFixed(2)}
            </span>
            <span className="text-[10px] text-slate-400">Closed Paper Trades</span>
          </div>
        </div>

        {/* 4. Active Positions & Margin */}
        <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-[11px] font-medium">
            <span>Active Positions</span>
            <Layers className="w-3.5 h-3.5 text-amber-400" />
          </div>
          <div className="mt-1">
            <span className="text-lg font-bold text-white font-mono block">
              {activePositions.length} / {statusData?.config?.max_active_positions ?? 5}
            </span>
            <span className="text-[10px] text-slate-400 font-mono">
              Margin: ${(wallet.allocated_margin_usd ?? 0).toFixed(0)} USDT
            </span>
          </div>
        </div>

        {/* 5. Win Rate */}
        <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-[11px] font-medium">
            <span>Bot Win Rate</span>
            <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
          </div>
          <div className="mt-1">
            <span className="text-lg font-bold text-white font-mono block">
              {wallet.win_rate_pct ?? 0}%
            </span>
            <span className="text-[10px] text-slate-400">
              {wallet.winning_trades_count ?? 0}W - {wallet.losing_trades_count ?? 0}L
            </span>
          </div>
        </div>

        {/* 6. Current Capital / Trade Parameter */}
        <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-[11px] font-medium">
            <span>Capital / Trade</span>
            <Settings className="w-3.5 h-3.5 text-indigo-400" />
          </div>
          <div className="mt-1">
            <span className="text-lg font-bold text-indigo-300 font-mono block">
              ${statusData?.config?.allocation_per_trade_usd ?? 250}
            </span>
            <span className="text-[10px] text-slate-400 font-mono">
              TP: +{statusData?.config?.take_profit_pct ?? 12}% | SL: -{statusData?.config?.stop_loss_pct ?? 5}%
            </span>
          </div>
        </div>

      </div>

      {/* Live Active Positions Table (if any) */}
      {activePositions.length > 0 && (
        <div className="mt-6 pt-5 border-t border-slate-800">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <Activity className="w-4 h-4 text-emerald-400" /> Live Autonomous Open Positions ({activePositions.length})
            </h3>
            <span className="text-[11px] text-slate-400 font-mono">Real-time mark-to-market ticking PnL</span>
          </div>

          <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950/60">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/80 text-slate-400 uppercase text-[10px] border-b border-slate-800">
                <tr>
                  <th className="px-4 py-2.5">Asset</th>
                  <th className="px-3 py-2.5">Entry Price</th>
                  <th className="px-3 py-2.5">Current Price</th>
                  <th className="px-3 py-2.5">Size ($USDT)</th>
                  <th className="px-3 py-2.5">TP / SL Target</th>
                  <th className="px-3 py-2.5">Live PnL</th>
                  <th className="px-4 py-2.5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {activePositions.map((t: any) => (
                  <tr key={t.trade_id} className="hover:bg-slate-900/40 transition">
                    <td className="px-4 py-3 font-bold text-white flex items-center gap-2">
                      <span className="text-indigo-400">{t.symbol}</span>
                      <span className="px-1.5 py-0.2 text-[9px] rounded bg-slate-800 text-slate-300 font-sans">{t.category}</span>
                    </td>
                    <td className="px-3 py-3 text-slate-300">${t.entry_price < 0.01 ? t.entry_price.toFixed(6) : t.entry_price.toFixed(4)}</td>
                    <td className="px-3 py-3 text-white font-bold">${t.current_price < 0.01 ? t.current_price.toFixed(6) : t.current_price.toFixed(4)}</td>
                    <td className="px-3 py-3 text-slate-300">${t.position_size_usd}</td>
                    <td className="px-3 py-3 text-slate-400 text-[11px]">
                      <span className="text-emerald-400">TP: ${t.take_profit_price < 0.01 ? t.take_profit_price.toFixed(6) : t.take_profit_price.toFixed(4)}</span>
                      <span className="text-slate-600 mx-1">|</span>
                      <span className="text-rose-400">SL: ${t.stop_loss_price < 0.01 ? t.stop_loss_price.toFixed(6) : t.stop_loss_price.toFixed(4)}</span>
                    </td>
                    <td className="px-3 py-3">
                      <span className={`font-bold ${(t.unrealized_pnl_usd ?? 0) >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                        {(t.unrealized_pnl_usd ?? 0) >= 0 ? "+" : ""}${(t.unrealized_pnl_usd ?? 0).toFixed(2)} ({t.roi_pct >= 0 ? "+" : ""}{t.roi_pct}%)
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => handleCloseTrade(t.trade_id)}
                        className="px-2.5 py-1 rounded-lg bg-rose-500/15 hover:bg-rose-500/25 text-rose-300 text-[11px] font-sans font-bold border border-rose-500/30 transition"
                      >
                        Exit Now
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* PARAMETERS CONFIGURATION MODAL */}
      {showConfigModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-lg w-full p-6 shadow-2xl animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Sliders className="w-5 h-5 text-indigo-400" /> Spot Autonomous Bot Parameters
              </h3>
              <button onClick={() => setShowConfigModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveConfig} className="space-y-4 pt-4 text-xs">
              
              {/* Capital Allocation Per Trade */}
              <div>
                <label className="block text-slate-300 font-semibold mb-1">
                  Virtual Capital Allocation Per Trade ($USDT):
                </label>
                <div className="flex items-center gap-2 mb-2">
                  {[50, 100, 250, 500, 1000].map((amt) => (
                    <button
                      key={amt}
                      type="button"
                      onClick={() => setCapitalPerTrade(amt)}
                      className={`px-3 py-1 rounded-lg text-xs font-mono font-bold transition border ${
                        capitalPerTrade === amt
                          ? "bg-indigo-600 text-white border-indigo-500"
                          : "bg-slate-800 text-slate-400 border-slate-700 hover:text-white"
                      }`}
                    >
                      ${amt}
                    </button>
                  ))}
                </div>
                <input
                  type="number"
                  value={capitalPerTrade}
                  onChange={(e) => setCapitalPerTrade(Number(e.target.value))}
                  min={10}
                  max={5000}
                  step={10}
                  className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-700 text-white font-mono focus:outline-none focus:border-indigo-500"
                  required
                />
              </div>

              {/* Max Active Positions & Min Opp Score */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Max Active Positions:</label>
                  <input
                    type="number"
                    value={maxPositions}
                    onChange={(e) => setMaxPositions(Number(e.target.value))}
                    min={1}
                    max={20}
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-700 text-white font-mono focus:outline-none focus:border-indigo-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Min AI Opportunity Score (0-100):</label>
                  <input
                    type="number"
                    value={minOppScore}
                    onChange={(e) => setMinOppScore(Number(e.target.value))}
                    min={40}
                    max={95}
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-700 text-white font-mono focus:outline-none focus:border-indigo-500"
                    required
                  />
                </div>
              </div>

              {/* TP % & SL % */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-emerald-400 font-semibold mb-1">Take Profit Target (%):</label>
                  <input
                    type="number"
                    value={tpPct}
                    onChange={(e) => setTpPct(Number(e.target.value))}
                    min={2}
                    max={100}
                    step={0.5}
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-700 text-white font-mono focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-rose-400 font-semibold mb-1">Stop Loss Limit (%):</label>
                  <input
                    type="number"
                    value={slPct}
                    onChange={(e) => setSlPct(Number(e.target.value))}
                    min={1}
                    max={50}
                    step={0.5}
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-700 text-white font-mono focus:outline-none focus:border-rose-500"
                    required
                  />
                </div>
              </div>

              {/* Auto Learn Toggle */}
              <div className="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-between">
                <div>
                  <span className="font-bold text-indigo-300 block">AI Self-Learning Engine</span>
                  <span className="text-[11px] text-slate-400">Dynamically tune category weights based on trade outcomes</span>
                </div>
                <input
                  type="checkbox"
                  checked={autoLearn}
                  onChange={(e) => setAutoLearn(e.target.checked)}
                  className="w-4 h-4 accent-indigo-500 rounded"
                />
              </div>

              {/* Submit Buttons */}
              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowConfigModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={updating}
                  className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold shadow-lg shadow-indigo-600/30"
                >
                  {updating ? "Saving..." : "Save Parameters"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* LEARNED LESSONS MODAL */}
      {showLessonsModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-2xl w-full p-6 shadow-2xl max-h-[85vh] flex flex-col animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Brain className="w-5 h-5 text-cyan-400" /> AI Continuous Self-Learning Insights Ledger
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">Lessons extracted from live paper trade outcomes &amp; dynamic weight adjustments.</p>
              </div>
              <button onClick={() => setShowLessonsModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="overflow-y-auto space-y-3 py-4 flex-1">
              {lessons.length === 0 ? (
                <div className="text-center py-10 text-slate-500 text-xs">
                  <Brain className="w-8 h-8 mx-auto mb-2 text-slate-600" />
                  No paper trade lessons recorded yet. The bot will automatically analyze and log insights as paper positions hit TP / SL!
                </div>
              ) : (
                lessons.map((lsn: any) => (
                  <div key={lsn.lesson_id} className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-white text-xs">{lsn.symbol}</span>
                        <span className="px-1.5 py-0.5 text-[10px] font-semibold rounded bg-slate-800 text-slate-300">{lsn.category}</span>
                        <span className={`px-2 py-0.2 text-[10px] font-bold rounded ${
                          lsn.outcome === "WIN_TP" ? "bg-emerald-500/20 text-emerald-300" : "bg-rose-500/20 text-rose-300"
                        }`}>
                          {lsn.outcome}
                        </span>
                      </div>
                      <span className={`text-xs font-mono font-bold ${lsn.pnl_usd >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                        {lsn.pnl_usd >= 0 ? "+" : ""}${lsn.pnl_usd.toFixed(2)} ({lsn.pnl_pct >= 0 ? "+" : ""}{lsn.pnl_pct.toFixed(2)}%)
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed">{lsn.lesson_text}</p>
                  </div>
                ))
              )}
            </div>

            <div className="pt-3 border-t border-slate-800 text-right">
              <button
                onClick={() => setShowLessonsModal(false)}
                className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700 text-xs font-bold"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
