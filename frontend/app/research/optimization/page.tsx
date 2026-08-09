"use client";

import React from "react";

export default function BayesianOptimizationPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Bayesian Hyperparameter Search</h1>
        <p className="text-gray-400 mt-1">Gaussian Process / TPE hyperparameter optimization convergence plots.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-emerald-400 font-bold">BAYES-OPTIMIZED</span>
            <h3 className="text-base font-semibold text-white mt-1">Optimal Parameters (50 Trials)</h3>
            <p className="text-xs text-gray-400">Fast EMA: 14 | Slow EMA: 28 | ATR Mult: 2.2 | Stop-Loss: 1.5%</p>
          </div>
          <span className="text-xs bg-indigo-950 text-indigo-300 border border-indigo-700 px-3 py-1 rounded">SHARPE: 2.78</span>
        </div>
      </div>
    </div>
  );
}
