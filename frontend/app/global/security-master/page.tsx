"use client";

import React from "react";

export default function SecurityMasterPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Security Master & Canonical Asset Registry</h1>
        <p className="text-gray-400 mt-1">Multi-asset security master across Crypto, Equities, Futures, Options, & Forex.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-400">
            <thead className="bg-black/50 text-gray-300 uppercase text-xs">
              <tr>
                <th className="px-4 py-3">Asset ID</th>
                <th className="px-4 py-3">Asset Class</th>
                <th className="px-4 py-3">Exchange</th>
                <th className="px-4 py-3">Tick / Lot Size</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-gray-800">
                <td className="px-4 py-3 font-mono text-emerald-400 font-bold">BTCUSDT</td>
                <td className="px-4 py-3 text-white font-bold">CRYPTO</td>
                <td className="px-4 py-3">BINANCE</td>
                <td className="px-4 py-3">0.01 / 0.0001</td>
              </tr>
              <tr className="border-b border-gray-800">
                <td className="px-4 py-3 font-mono text-indigo-400 font-bold">AAPL</td>
                <td className="px-4 py-3 text-white font-bold">EQUITY</td>
                <td className="px-4 py-3">NASDAQ</td>
                <td className="px-4 py-3">0.01 / 1.0</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
