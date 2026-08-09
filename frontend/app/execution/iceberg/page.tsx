"use client";

import React from "react";

export default function IcebergConsolePage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Iceberg Order Console</h1>
        <p className="text-gray-400 mt-1">Disclosed vs hidden reserve quantity and anti-detection refill monitor.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">ICEBERG REPLENISHMENT</span>
            <h3 className="text-lg font-bold text-white mt-1">Visible: 5.0 BTC | Hidden Reserve: 45.0 BTC</h3>
            <p className="text-xs text-gray-400">Total Size: 50.0 BTC | Refills Completed: 0</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">RESERVE PROTECTED</span>
        </div>
      </div>
    </div>
  );
}
