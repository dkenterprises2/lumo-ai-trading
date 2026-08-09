"use client";

import React from "react";

export default function NaturalLanguageStrategyBuilderPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Natural Language Strategy Builder</h1>
        <p className="text-gray-400 mt-1">Transform plain-English trading prompts into executable DSL specifications & backtests.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
        <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
          <span className="text-xs text-gray-400 font-medium">Natural Language Input Prompt</span>
          <p className="text-sm text-indigo-300 font-mono mt-1">"Create a BTC trend-following strategy using 20-day momentum and ATR-based stops at 2.0 ATR."</p>
        </div>
        <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
          <span className="text-xs text-gray-400 font-medium">Generated Strategy DSL</span>
          <pre className="text-xs text-emerald-400 font-mono mt-1">strategy_btc_momentum_v1 = MomentumStrategy(symbol='BTCUSDT', lookback=20, stop_loss_atr=2.0)</pre>
        </div>
        <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded text-xs font-bold">Submit to Backtest & Research</button>
      </div>
    </div>
  );
}
