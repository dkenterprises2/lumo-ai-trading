"use client";

import React from "react";

export default function TradeBlotterGridPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Institutional Real-Time Trade Blotter</h1>
        <p className="text-gray-400 mt-1">Real-time trade blotter grid, multi-account allocations, & filter controls.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-black/50 text-gray-400 font-mono">
            <tr>
              <th className="p-3">ORDER ID</th>
              <th className="p-3">SYMBOL</th>
              <th className="p-3">SIDE</th>
              <th className="p-3">QUANTITY</th>
              <th className="p-3">PRICE</th>
              <th className="p-3">STATUS</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800 text-gray-200 font-mono">
            <tr>
              <td className="p-3 text-indigo-400 font-bold">ord_p23_101</td>
              <td className="p-3">BTCUSDT</td>
              <td className="p-3 text-emerald-400 font-bold">BUY</td>
              <td className="p-3">2.50</td>
              <td className="p-3">$64,800.00</td>
              <td className="p-3"><span className="bg-emerald-950 text-emerald-300 border border-emerald-700 px-2 py-0.5 rounded text-[10px]">FILLED</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
