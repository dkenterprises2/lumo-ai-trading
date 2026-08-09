"use client";

import React from "react";

export default function WalkForwardPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Walk-Forward Optimization Console</h1>
        <p className="text-gray-400 mt-1">Rolling-window in-sample optimization & out-of-sample performance validation.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">WFO-2026-RUN1</span>
            <h3 className="text-base font-semibold text-white mt-1">DualEMA_MeanReversion (6 Windows Evaluated)</h3>
            <p className="text-xs text-gray-400">In-Sample Sharpe: 2.45 | Out-of-Sample Sharpe: 2.12</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">EFFICIENCY: 86.5%</span>
        </div>
      </div>
    </div>
  );
}
