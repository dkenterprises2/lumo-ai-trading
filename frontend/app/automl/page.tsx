"use client";

import React from "react";

export default function AutoMLStrategyGeneratorPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">AutoML Strategy Generator & Search Space</h1>
        <p className="text-gray-400 mt-1">Automatic feature selection, indicator search space exploration, & model templates.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">AUTOML RUN: CAND_AUTOML_101</span>
            <h3 className="text-lg font-bold text-white mt-1">Indicators: SMA_20 + RSI_14 + ATR_14</h3>
            <p className="text-xs text-gray-400">Estimated Sharpe: 2.25 | Max Drawdown: 8.0%</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">CANDIDATE GENERATED</span>
        </div>
      </div>
    </div>
  );
}
