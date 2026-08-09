"use client";

import React from "react";

export default function ModelRegistryPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Model Registry & Lifecycle Management</h1>
        <p className="text-gray-400 mt-1">Staging, Production promotion, and Canary rollout controls.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Registered Models</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-400">
            <thead className="bg-black/50 text-gray-300 uppercase text-xs">
              <tr>
                <th className="px-4 py-3">Model ID</th>
                <th className="px-4 py-3">Model Name</th>
                <th className="px-4 py-3">Version</th>
                <th className="px-4 py-3">Stage</th>
                <th className="px-4 py-3">Accuracy</th>
                <th className="px-4 py-3">Sharpe</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-gray-800">
                <td className="px-4 py-3 font-mono text-white">MOD-XGB-2026</td>
                <td className="px-4 py-3 font-semibold text-white">XGBoost Alpha Predictor</td>
                <td className="px-4 py-3">2.1.0</td>
                <td className="px-4 py-3 text-emerald-400 font-bold">PRODUCTION</td>
                <td className="px-4 py-3">68.4%</td>
                <td className="px-4 py-3">2.45</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
