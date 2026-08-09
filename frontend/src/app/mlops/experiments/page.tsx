"use client";

import React from "react";

export default function ExperimentsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">MLFlow Experiment Tracking</h1>
        <p className="text-gray-400 mt-1">Track training runs, hyperparameters, loss curves, and model metrics.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Active Experiments</h2>
        <div className="border border-gray-800 rounded-lg p-4 bg-black/40">
          <div className="flex justify-between items-center">
            <div>
              <span className="font-mono text-xs text-indigo-400 font-bold">EXP-101</span>
              <h3 className="text-lg font-bold text-white mt-1">BTC-USDT Momentum & Volatility Model</h3>
              <p className="text-sm text-gray-400">AutoML training with XGBoost and LSTM ensemble</p>
            </div>
            <span className="text-xs bg-indigo-900/60 text-indigo-300 px-3 py-1 rounded-full border border-indigo-700">3 Runs Logged</span>
          </div>
        </div>
      </div>
    </div>
  );
}
