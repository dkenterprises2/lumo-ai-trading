"use client";

import React from "react";

export default function AlgoBenchmarksPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Execution Algorithm Benchmarks</h1>
        <p className="text-gray-400 mt-1">Comparative performance evaluation (TWAP vs VWAP vs POV vs Iceberg).</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-400">
            <thead className="bg-black/50 text-gray-300 uppercase text-xs">
              <tr>
                <th className="px-4 py-3">Algorithm</th>
                <th className="px-4 py-3">Slippage (bps)</th>
                <th className="px-4 py-3">Execution Time</th>
                <th className="px-4 py-3">Rank</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-gray-800">
                <td className="px-4 py-3 font-bold text-emerald-400">VWAP</td>
                <td className="px-4 py-3 text-white font-bold">1.8 bps</td>
                <td className="px-4 py-3">3,600s</td>
                <td className="px-4 py-3 text-emerald-400 font-bold">WINNER (1st)</td>
              </tr>
              <tr className="border-b border-gray-800">
                <td className="px-4 py-3 font-bold text-white">TWAP</td>
                <td className="px-4 py-3 text-white">2.4 bps</td>
                <td className="px-4 py-3">3,600s</td>
                <td className="px-4 py-3 text-gray-300">2nd</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
