"use client";

import React from "react";

export default function BayesianOptimizationPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Bayesian Hyperparameter Optimization</h1>
        <p className="text-gray-400 mt-1">Gaussian Process surrogate models, Expected Improvement acquisition, & parameter convergence.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-amber-400 font-bold">BAYES OPT: ALPHA_MOMENTUM_V12</span>
            <h3 className="text-lg font-bold text-white mt-1">Best Params: Lookback=14, Entry=2.1, StopLoss=2%</h3>
            <p className="text-xs text-gray-400">Best Sharpe: 2.52 | Trials Completed: 100</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">CONVERGED</span>
        </div>
      </div>
    </div>
  );
}
