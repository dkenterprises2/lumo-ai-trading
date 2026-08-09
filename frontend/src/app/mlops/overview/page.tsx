"use client";

import React from "react";

export default function MLOpsOverviewPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">MLOps & Autonomous AI Operations Platform</h1>
        <p className="text-gray-400 mt-1">Lifecycle orchestration, automated retraining, drift detection, and model governance.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="text-sm text-gray-400 font-medium">Active Production Model</div>
          <div className="text-xl font-bold text-emerald-400 mt-2">XGBoost Alpha Predictor (v2.1.0)</div>
          <div className="text-xs text-gray-500 mt-1">Sharpe: 2.45 | Accuracy: 68.4%</div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="text-sm text-gray-400 font-medium">Drift Status (PSI)</div>
          <div className="text-xl font-bold text-amber-400 mt-2">MODERATE DRIFT (0.12)</div>
          <div className="text-xs text-gray-500 mt-1">Retraining Recommended</div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="text-sm text-gray-400 font-medium">Shadow Deployment</div>
          <div className="text-xl font-bold text-indigo-400 mt-2">MOD-CANDIDATE-01</div>
          <div className="text-xs text-gray-500 mt-1">100% Traffic Mirrored</div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="text-sm text-gray-400 font-medium">GPU Acceleration</div>
          <div className="text-xl font-bold text-purple-400 mt-2">CUDA Accelerated</div>
          <div className="text-xs text-gray-500 mt-1">Avg Latency: 3.4ms</div>
        </div>
      </div>
    </div>
  );
}
