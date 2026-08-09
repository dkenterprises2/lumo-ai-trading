"use client";

import React from "react";

export default function ExecutionOrdersPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Active Algorithmic Orders</h1>
        <p className="text-gray-400 mt-1">Real-time parent order progress and active slice monitors.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-400">
            <thead className="bg-black/50 text-gray-300 uppercase text-xs">
              <tr>
                <th className="px-4 py-3">Order ID</th>
                <th className="px-4 py-3">Algorithm</th>
                <th className="px-4 py-3">Symbol</th>
                <th className="px-4 py-3">Progress</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-gray-800">
                <td className="px-4 py-3 font-mono text-indigo-400 font-bold">EXEC-ORD-101</td>
                <td className="px-4 py-3 font-bold text-white">TWAP</td>
                <td className="px-4 py-3">BTC/USDT</td>
                <td className="px-4 py-3 text-emerald-400 font-bold">4.5 / 10.0 (45%)</td>
                <td className="px-4 py-3 text-emerald-400 font-bold">RUNNING</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
