"use client";

import React, { useState } from "react";
import { ArrowDownRight, ArrowUpRight, ClipboardList } from "lucide-react";

interface ManualOrderFormProps {
  symbol: string;
  currentPrice: number | null;
  onSubmitOrder: (side: "LONG" | "SHORT", allocationUsd: number, leverage: number, orderType: string) => void;
}

export function ManualOrderForm({ symbol, currentPrice, onSubmitOrder }: ManualOrderFormProps) {
  const [orderType, setOrderType] = useState("MARKET");
  const [amountUsdt, setAmountUsdt] = useState(1000);
  const [leverage, setLeverage] = useState(2);
  const canSubmit = currentPrice !== null && Number.isFinite(amountUsdt) && amountUsdt > 0 && leverage >= 1;

  return (
    <div className="space-y-4 rounded-2xl border border-slate-800/80 bg-slate-900/60 p-5 shadow-xl backdrop-blur-xl">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-cyan-500/10 text-cyan-400">
            <ClipboardList className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100">Execution Panel</h3>
            <p className="text-xs text-slate-400">{symbol} • {currentPrice === null ? "Price feed unavailable" : `$${currentPrice.toFixed(2)}`}</p>
          </div>
        </div>
      </div>

      <div className="space-y-4 text-xs">
        <div className="flex items-center justify-between gap-2">
          <span className="font-medium text-slate-400">Order Type</span>
          <select value={orderType} onChange={(event) => setOrderType(event.target.value)} className="rounded-xl border border-slate-800 bg-slate-950 px-3 py-1.5 font-semibold text-slate-200 focus:outline-none">
            <option value="MARKET">MARKET</option>
            <option value="LIMIT">LIMIT</option>
          </select>
        </div>

        <div className="space-y-1">
          <div className="flex justify-between text-slate-400">
            <span>Notional Value (USDT)</span>
            <span className="font-mono text-cyan-400">${Number.isFinite(amountUsdt) ? amountUsdt : "—"}</span>
          </div>
          <input type="number" min="0.01" step="0.01" value={Number.isFinite(amountUsdt) ? amountUsdt : ""} onChange={(event) => setAmountUsdt(event.target.valueAsNumber)} className="w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 font-mono font-bold text-slate-100 focus:border-cyan-500 focus:outline-none" />
        </div>

        <div className="space-y-1">
          <div className="flex justify-between text-slate-400">
            <span>Leverage</span>
            <span className="font-mono font-bold text-amber-400">{leverage}x</span>
          </div>
          <input type="range" min={1} max={25} value={leverage} onChange={(event) => setLeverage(Number(event.target.value))} className="w-full cursor-pointer accent-cyan-400" />
          <div className="flex justify-between font-mono text-[10px] text-slate-500"><span>1x</span><span>5x</span><span>10x</span><span>25x</span></div>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-950 p-2.5 text-[11px] text-slate-400">
          Margin and protective targets are assigned and recorded by the backend risk engine when this order executes.
        </div>

        <div className="grid grid-cols-2 gap-3 pt-2">
          <button onClick={() => onSubmitOrder("LONG", amountUsdt, leverage, orderType)} disabled={!canSubmit} className="flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 px-4 py-3 text-sm font-bold text-white shadow-lg shadow-emerald-500/20 transition-all hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-40">
            <ArrowUpRight className="h-4 w-4" /><span>BUY / LONG</span>
          </button>
          <button onClick={() => onSubmitOrder("SHORT", amountUsdt, leverage, orderType)} disabled={!canSubmit} className="flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-rose-500 to-pink-600 px-4 py-3 text-sm font-bold text-white shadow-lg shadow-rose-500/20 transition-all hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-40">
            <ArrowDownRight className="h-4 w-4" /><span>SELL / SHORT</span>
          </button>
        </div>
      </div>
    </div>
  );
}
