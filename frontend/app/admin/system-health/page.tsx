"use client";

import React from "react";

export default function AdminSystemHealthPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">System & Cluster Health</h1>
        <p className="text-gray-400 mt-1">Exchanges, Redis cluster, WebSocket nodes, and database status.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
        <div className="flex justify-between items-center border-b border-gray-800 pb-3">
          <span className="text-white font-medium">Database Persistence (SQLite/PostgreSQL)</span>
          <span className="text-emerald-400 font-bold">ONLINE</span>
        </div>
        <div className="flex justify-between items-center border-b border-gray-800 pb-3">
          <span className="text-white font-medium">Redis Pub/Sub Stream Cluster</span>
          <span className="text-emerald-400 font-bold">ONLINE</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-white font-medium">Exchange Adapters (Binance / Bybit / OKX)</span>
          <span className="text-emerald-400 font-bold">CONNECTED</span>
        </div>
      </div>
    </div>
  );
}
