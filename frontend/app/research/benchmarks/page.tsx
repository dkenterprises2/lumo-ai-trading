"use client";

import React from "react";

export default function BenchmarksPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Institutional Strategy Benchmarking</h1>
        <p className="text-gray-400 mt-1">Benchmark comparison against Buy & Hold BTC/ETH indexes.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-400">
            <thead className="bg-black/50 text-gray-300 uppercase text-xs">
              <tr>
                <th className="px-4 py-3">Strategy / Benchmark</th>
                <th className="px-4 py-3">Ann. Return</th>
                <th className="px-4 py-3">Sharpe</th>
                <th className="px-4 py-3">Max Drawdown</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-gray-800">
                <td className="px-4 py-3 font-bold text-emerald-400">Lumo Quant Multi-Factor</td>
                <td className="px-4 py-3 text-white font-bold">+64.8%</td>
                <td className="px-4 py-3 text-emerald-400 font-bold">2.85</td>
                <td className="px-4 py-3 text-gray-300">-12.4%</td>
              </tr>
              <tr className="border-b border-gray-800">
                <td className="px-4 py-3 font-bold text-gray-300">BTC Buy & Hold</td>
                <td className="px-4 py-3 text-white">+42.5%</td>
                <td className="px-4 py-3 text-gray-400">1.15</td>
                <td className="px-4 py-3 text-red-400">-38.2%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
