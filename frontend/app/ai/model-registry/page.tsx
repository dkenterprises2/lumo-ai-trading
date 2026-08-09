"use client";

import React from "react";

export default function AIModelRegistryPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">AI Model Registry & Checkpoints</h1>
        <p className="text-gray-400 mt-1">Versioned agent checkpoints, evaluation metrics, & promotional status.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-400">
            <thead className="bg-black/50 text-gray-300 uppercase text-xs">
              <tr>
                <th className="px-4 py-3">Version ID</th>
                <th className="px-4 py-3">Agent</th>
                <th className="px-4 py-3">Sharpe Ratio</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-gray-800">
                <td className="px-4 py-3 font-mono text-indigo-400 font-bold">ppo_bull_v1</td>
                <td className="px-4 py-3 text-white">PPO_BULL_SPECIALIST</td>
                <td className="px-4 py-3 text-emerald-400 font-bold">2.45</td>
                <td className="px-4 py-3 text-emerald-400 font-bold">APPROVED</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
