"use client";

import React from "react";

export default function AIAgentsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Market-Regime Specialist Agents</h1>
        <p className="text-gray-400 mt-1">Specialized RL agents for bull, bear, sideways, and high-volatility regimes.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="flex justify-between items-center">
            <div>
              <span className="text-xs text-emerald-400 font-bold font-mono">BULL SPECIALIST</span>
              <h2 className="text-lg font-bold text-white mt-1">Trend Following Agent</h2>
              <p className="text-xs text-gray-400">Action: BUY_SMALL | Sharpe: 2.45</p>
            </div>
            <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">ACTIVE</span>
          </div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="flex justify-between items-center">
            <div>
              <span className="text-xs text-indigo-400 font-bold font-mono">SIDEWAYS SPECIALIST</span>
              <h2 className="text-lg font-bold text-white mt-1">Mean Reversion Agent</h2>
              <p className="text-xs text-gray-400">Action: HOLD | Sharpe: 1.95</p>
            </div>
            <span className="text-xs bg-indigo-950 text-indigo-300 border border-indigo-700 px-3 py-1 rounded">ACTIVE</span>
          </div>
        </div>
      </div>
    </div>
  );
}
