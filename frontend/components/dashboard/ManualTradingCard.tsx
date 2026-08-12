"use client";

import React, { useState } from "react";
import { Zap, ArrowUpRight, ArrowDownRight, DollarSign, ShieldAlert, CheckCircle2, AlertCircle, RefreshCw } from "lucide-react";
import { submitOrder } from "@/services/api";

const TOP_SYMBOLS = [
  "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", 
  "ADA/USDT", "DOGE/USDT", "AVAX/USDT", "LINK/USDT", "ARB/USDT",
  "SUI/USDT", "INJ/USDT", "TIA/USDT", "UNI/USDT", "NEAR/USDT",
  "APT/USDT", "OP/USDT", "LTC/USDT", "DOT/USDT", "PEPE/USDT"
];

interface ManualTradingCardProps {
  onOrderExecuted?: () => void;
  currentPrices?: Record<string, number>;
}

export const ManualTradingCard: React.FC<ManualTradingCardProps> = ({ onOrderExecuted, currentPrices }) => {
  const [symbol, setSymbol] = useState<string>("BTC/USDT");
  const [side, setSide] = useState<"LONG" | "SHORT">("LONG");
  const [orderType, setOrderType] = useState<string>("MARKET");
  const [allocationUsd, setAllocationUsd] = useState<number>(5000);
  const [leverage, setLeverage] = useState<number>(2);
  const [stopLossPct, setStopLossPct] = useState<number>(2.5);
  const [takeProfitPct, setTakeProfitPct] = useState<number>(5.0);

  const [loading, setLoading] = useState<boolean>(false);
  const [message, setMessage] = useState<{ text: string; type: "success" | "error" } | null>(null);

  const activePrice = currentPrices?.[symbol] ?? 0;

  const calculatedSlPrice = activePrice > 0 
    ? (side === "LONG" ? activePrice * (1 - stopLossPct / 100) : activePrice * (1 + stopLossPct / 100))
    : 0;

  const calculatedTpPrice = activePrice > 0 
    ? (side === "LONG" ? activePrice * (1 + takeProfitPct / 100) : activePrice * (1 - takeProfitPct / 100))
    : 0;

  const handleExecute = async () => {
    setLoading(true);
    setMessage(null);

    try {
      const res = await submitOrder({
        symbol,
        side,
        order_type: orderType,
        allocation_usd: allocationUsd,
        leverage,
        stop_loss_price: calculatedSlPrice > 0 ? Number(calculatedSlPrice.toFixed(4)) : null,
        take_profit_price: calculatedTpPrice > 0 ? Number(calculatedTpPrice.toFixed(4)) : null,
      });

      if (res.status === "success") {
        setMessage({ text: res.message || `Manual ${side} order placed for ${symbol}`, type: "success" });
        if (onOrderExecuted) onOrderExecuted();
      } else {
        setMessage({ text: res.message || "Failed to execute order", type: "error" });
      }
    } catch (err: any) {
      setMessage({ text: err.message || "Error submitting manual order", type: "error" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800/90 p-5 rounded-3xl shadow-xl backdrop-blur-xl hover:border-slate-700/80 transition-all flex flex-col justify-between h-full">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-800/80 mb-4">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              <Zap className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white tracking-wide">Manual Quick Order Terminal</h3>
              <p className="text-[10px] text-slate-400">Institutional Direct Execution Router</p>
            </div>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            FAST EXECUTE
          </span>
        </div>

        {/* Side & Symbol Selection Row */}
        <div className="grid grid-cols-2 gap-3 mb-3">
          {/* LONG / SHORT Toggle */}
          <div className="bg-slate-950/60 p-1 rounded-2xl border border-slate-800/80 flex gap-1">
            <button
              onClick={() => setSide("LONG")}
              className={`flex-1 py-1.5 rounded-xl font-extrabold text-xs transition-all flex items-center justify-center gap-1 ${
                side === "LONG"
                  ? "bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/20"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <ArrowUpRight className="w-3.5 h-3.5" /> LONG
            </button>
            <button
              onClick={() => setSide("SHORT")}
              className={`flex-1 py-1.5 rounded-xl font-extrabold text-xs transition-all flex items-center justify-center gap-1 ${
                side === "SHORT"
                  ? "bg-rose-500 text-slate-950 shadow-lg shadow-rose-500/20"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <ArrowDownRight className="w-3.5 h-3.5" /> SHORT
            </button>
          </div>

          {/* Symbol Select */}
          <div className="relative">
            <select
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="w-full h-full bg-slate-950/80 border border-slate-800 text-slate-100 font-mono font-bold text-xs rounded-2xl px-3 py-1.5 focus:border-cyan-500 focus:outline-none cursor-pointer"
            >
              {TOP_SYMBOLS.map((sym) => (
                <option key={sym} value={sym} className="bg-slate-900 text-slate-100 font-mono">
                  {sym}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Price & Order Type Bar */}
        <div className="flex items-center justify-between bg-slate-950/50 p-2.5 rounded-2xl border border-slate-800/60 mb-3 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="text-[10px] uppercase text-slate-400 font-semibold">Live Price:</span>
            <span className="font-mono font-extrabold text-cyan-400">
              {activePrice > 0 ? `$${activePrice.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 4 })}` : "Fetching..."}
            </span>
          </div>

          <div className="flex gap-1">
            {["MARKET", "LIMIT"].map((t) => (
              <button
                key={t}
                onClick={() => setOrderType(t)}
                className={`px-2 py-0.5 rounded-lg text-[10px] font-bold transition-all ${
                  orderType === t
                    ? "bg-indigo-600 text-white"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        {/* Allocation & Leverage Controls */}
        <div className="grid grid-cols-2 gap-3 mb-3">
          {/* Amount per Trade */}
          <div>
            <label className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Amount (USDT)
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 font-mono text-xs">$</span>
              <input
                type="number"
                value={allocationUsd}
                onChange={(e) => setAllocationUsd(Math.max(10, Number(e.target.value)))}
                className="w-full bg-slate-950/80 border border-slate-800 text-white font-mono font-bold text-xs rounded-xl pl-7 pr-3 py-1.5 focus:border-cyan-500 focus:outline-none"
              />
            </div>
            <div className="flex gap-1 mt-1">
              {[1000, 2500, 5000, 10000].map((amt) => (
                <button
                  key={amt}
                  onClick={() => setAllocationUsd(amt)}
                  className="flex-1 text-[9px] font-mono bg-slate-800/60 hover:bg-slate-800 text-slate-300 rounded py-0.5 transition-all"
                >
                  ${amt >= 1000 ? `${amt / 1000}k` : amt}
                </button>
              ))}
            </div>
          </div>

          {/* Leverage */}
          <div>
            <label className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Leverage Multiplier
            </label>
            <select
              value={leverage}
              onChange={(e) => setLeverage(Number(e.target.value))}
              className="w-full bg-slate-950/80 border border-slate-800 text-amber-400 font-mono font-bold text-xs rounded-xl px-3 py-1.5 focus:border-cyan-500 focus:outline-none"
            >
              {[1, 2, 3, 5, 10, 15, 20, 25].map((lev) => (
                <option key={lev} value={lev} className="bg-slate-900 text-slate-100">
                  {lev}x Leverage
                </option>
              ))}
            </select>
            <div className="text-[9px] text-slate-400 mt-1 font-mono">
              Margin: <span className="text-white font-bold">${(allocationUsd / leverage).toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* SL / TP Quick Targets */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="bg-slate-950/40 p-2 rounded-xl border border-slate-800/50">
            <div className="flex justify-between text-[10px] font-semibold text-slate-400 mb-1">
              <span className="text-rose-400">Stop Loss</span>
              <span>{stopLossPct}%</span>
            </div>
            <input
              type="range"
              min="0.5"
              max="10"
              step="0.5"
              value={stopLossPct}
              onChange={(e) => setStopLossPct(Number(e.target.value))}
              className="w-full accent-rose-500 h-1 bg-slate-800 rounded-lg cursor-pointer"
            />
            {calculatedSlPrice > 0 && (
              <div className="text-[9px] font-mono text-slate-400 mt-0.5 text-right">
                Target: ${calculatedSlPrice.toFixed(2)}
              </div>
            )}
          </div>

          <div className="bg-slate-950/40 p-2 rounded-xl border border-slate-800/50">
            <div className="flex justify-between text-[10px] font-semibold text-slate-400 mb-1">
              <span className="text-emerald-400">Take Profit</span>
              <span>{takeProfitPct}%</span>
            </div>
            <input
              type="range"
              min="1"
              max="25"
              step="0.5"
              value={takeProfitPct}
              onChange={(e) => setTakeProfitPct(Number(e.target.value))}
              className="w-full accent-emerald-500 h-1 bg-slate-800 rounded-lg cursor-pointer"
            />
            {calculatedTpPrice > 0 && (
              <div className="text-[9px] font-mono text-slate-400 mt-0.5 text-right">
                Target: ${calculatedTpPrice.toFixed(2)}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Execution Feedback & Action Button */}
      <div>
        {message && (
          <div
            className={`p-2.5 rounded-xl text-xs font-semibold flex items-center gap-2 mb-3 ${
              message.type === "success"
                ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
            }`}
          >
            {message.type === "success" ? <CheckCircle2 className="w-4 h-4 shrink-0" /> : <AlertCircle className="w-4 h-4 shrink-0" />}
            <span className="truncate">{message.text}</span>
          </div>
        )}

        <button
          onClick={handleExecute}
          disabled={loading}
          className={`w-full py-3 rounded-2xl font-extrabold text-xs tracking-wider transition-all shadow-lg flex items-center justify-center gap-2 ${
            side === "LONG"
              ? "bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-emerald-500/25"
              : "bg-rose-500 hover:bg-rose-400 text-slate-950 shadow-rose-500/25"
          } ${loading ? "opacity-75 cursor-not-allowed" : ""}`}
        >
          {loading ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" /> EXECUTING ORDER...
            </>
          ) : (
            <>
              <Zap className="w-4 h-4" /> EXECUTE {side} ORDER FOR {symbol}
            </>
          )}
        </button>
      </div>
    </div>
  );
};
