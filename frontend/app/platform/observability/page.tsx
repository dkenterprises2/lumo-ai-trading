"use client";

import React from "react";

export default function PlatformObservabilityPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Distributed Observability Stack</h1>
        <p className="text-gray-400 mt-1">Prometheus metrics, Grafana dashboards, Loki logs, & Tempo traces.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">HTTP P99 Latency</span>
            <div className="text-2xl font-bold text-emerald-400 mt-1">12.4 ms</div>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">WebSocket Connections</span>
            <div className="text-2xl font-bold text-indigo-400 mt-1">1,420 Active</div>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Orderbook Micro-Latency</span>
            <div className="text-2xl font-bold text-amber-400 mt-1">850 &mu;s</div>
          </div>
        </div>
      </div>
    </div>
  );
}
