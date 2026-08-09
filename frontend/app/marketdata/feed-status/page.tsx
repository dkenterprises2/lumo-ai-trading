"use client";

import React from "react";

export default function FeedStatusPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Exchange Feed Health Dashboard</h1>
        <p className="text-gray-400 mt-1">Multi-exchange WebSocket stream connection health and sequence resync log.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="space-y-3">
          <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
            <div>
              <span className="font-bold text-white">Binance Level-2 Stream</span>
              <p className="text-xs text-gray-400">1,450 Ticks/sec | Average Fanout Latency: 12.4 ms</p>
            </div>
            <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">CONNECTED</span>
          </div>
        </div>
      </div>
    </div>
  );
}
