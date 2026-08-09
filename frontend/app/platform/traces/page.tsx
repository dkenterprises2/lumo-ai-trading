"use client";

import React from "react";

export default function DistributedTracesPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Distributed Tracing & Jaeger</h1>
        <p className="text-gray-400 mt-1">OpenTelemetry trace propagation across microservices.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="bg-black/50 border border-gray-800 p-4 rounded-lg font-mono text-xs text-gray-300">
          <div className="text-indigo-400 font-bold mb-1">[TRACE-ID: trace-8f4e2a1b9c3d4e5f]</div>
          <div>api-gateway (1.2 ms) ──&gt; trading-service (8.4 ms) ──&gt; execution-service (14.2 ms)</div>
          <div className="text-emerald-400 mt-1">Total Latency: 23.8 ms | Status: OK</div>
        </div>
      </div>
    </div>
  );
}
