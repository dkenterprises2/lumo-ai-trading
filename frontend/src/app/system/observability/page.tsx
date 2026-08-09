"use client";

import React from "react";

export default function ObservabilityDashboardPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Observability & Metrics Console</h1>
        <p className="text-gray-400 mt-1">Prometheus metrics exporter, OpenTelemetry traces, and log correlation IDs.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Prometheus Metrics Exporter</h2>
          <pre className="bg-black/50 text-emerald-400 p-4 rounded-lg text-xs overflow-x-auto">
{`# HELP lumo_http_requests_total Total HTTP requests
lumo_http_requests_total{status="200"} 1420
lumo_active_websocket_connections 8
lumo_system_cpu_usage_pct 14.5`}
          </pre>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Redis Streams Pub/Sub Cluster</h2>
          <div className="space-y-3">
            <div className="flex justify-between border-b border-gray-800 pb-2">
              <span className="text-gray-400">Cluster Status</span>
              <span className="text-emerald-400 font-semibold">HEALTHY</span>
            </div>
            <div className="flex justify-between border-b border-gray-800 pb-2">
              <span className="text-gray-400">Active Channels</span>
              <span className="text-white font-semibold">4 Channels</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Memory Used</span>
              <span className="text-white font-semibold">14.2 MB</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
