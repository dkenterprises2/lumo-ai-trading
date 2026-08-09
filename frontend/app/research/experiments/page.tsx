"use client";

import React from "react";

export default function ResearchExperimentsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">MLflow Experiment Tracking Platform</h1>
        <p className="text-gray-400 mt-1">Git commit SHA, dataset snapshot ID, hyperparameter sweeps, & artifact tracking.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-emerald-400 font-bold">EXP_STAT_ARB_01</span>
            <h3 className="text-lg font-bold text-white mt-1">StatArb Pair Trading Sweep</h3>
            <p className="text-xs text-gray-400">Sharpe: 2.45 | Max Drawdown: 4.2% | Status: COMPLETED</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">COMPLETED</span>
        </div>
      </div>
    </div>
  );
}
