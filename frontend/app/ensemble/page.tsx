"use client";

import React from "react";

export default function EnsembleComposerPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Ensemble Strategy Composer</h1>
        <p className="text-gray-400 mt-1">Correlation-constrained & volatility-weighted multi-strategy portfolio ensembles.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">ENSEMBLE: ENS_ALPHA_MULTI_01</span>
            <h3 className="text-lg font-bold text-white mt-1">Momentum (50%) + StatArb Pairs (50%)</h3>
            <p className="text-xs text-gray-400">Ensemble Sharpe: 2.78 | Correlation Constraint: &lt; 0.35</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">COMPOSED</span>
        </div>
      </div>
    </div>
  );
}
