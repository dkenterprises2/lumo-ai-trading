"use client";

import React from "react";

export default function VenueLatencyPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Venue Latency Monitor</h1>
        <p className="text-gray-400 mt-1">Sub-millisecond API roundtrip latency and jitter tracking.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Binance Roundtrip</span>
            <div className="text-2xl font-bold text-emerald-400 mt-1">12.4 ms</div>
            <span className="text-xs text-gray-500">Jitter: 1.2 ms</span>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Bybit Roundtrip</span>
            <div className="text-2xl font-bold text-emerald-400 mt-1">18.2 ms</div>
            <span className="text-xs text-gray-500">Jitter: 2.1 ms</span>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">OKX Roundtrip</span>
            <div className="text-2xl font-bold text-emerald-400 mt-1">22.1 ms</div>
            <span className="text-xs text-gray-500">Jitter: 3.4 ms</span>
          </div>
        </div>
      </div>
    </div>
  );
}
