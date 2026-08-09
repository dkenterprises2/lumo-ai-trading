"use client";

import React from "react";

export default function PlatformTracesPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">OpenTelemetry Distributed Tracing</h1>
        <p className="text-gray-400 mt-1">End-to-end W3C TraceContext propagation across API, Execution, AI, & SaaS.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">TRACE ID: 4bf92f3577b34da6a3ce929d0e0e4736</span>
            <h3 className="text-base font-semibold text-white mt-1">POST /api/execution/orders (Total: 18.2ms)</h3>
            <p className="text-xs text-gray-400">Spans: API Gateway (2ms) &rarr; Risk Engine (4ms) &rarr; Execution Algo (12.2ms)</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">3 SPANS</span>
        </div>
      </div>
    </div>
  );
}
