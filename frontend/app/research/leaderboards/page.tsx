"use client";

import React from "react";

export default function ResearchLeaderboardsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Experiment Leaderboards & Model Ranking</h1>
        <p className="text-gray-400 mt-1">Sharpe ratio vs Max Drawdown scatter plot rankings across all quant models.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-amber-400 font-bold">RANK #1: RUN_001</span>
            <h3 className="text-lg font-bold text-white mt-1">StatArb Pair Strategy (Sharpe: 2.45)</h3>
            <p className="text-xs text-gray-400">Information Coefficient (IC): 0.092</p>
          </div>
          <span className="text-xs bg-amber-950 text-amber-300 border border-amber-700 px-3 py-1 rounded">RANK #1</span>
        </div>
      </div>
    </div>
  );
}
