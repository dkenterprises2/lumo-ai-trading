"use client";

import React from "react";

export default function AutoMLRunsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">AutoML Search Progress & Candidate Funnel</h1>
        <p className="text-gray-400 mt-1">Multi-objective AutoML search history, candidate ranking, & feature selection.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-emerald-400 font-bold">RUN_ID: AUTOML_RUN_101</span>
            <h3 className="text-base font-semibold text-white mt-1">Candidates Evaluated: 1,420 | Top Sharpe: 2.25</h3>
            <p className="text-xs text-gray-400">Search Space: SMA/EMA/RSI/MACD Combinations</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">RUN COMPLETED</span>
        </div>
      </div>
    </div>
  );
}
