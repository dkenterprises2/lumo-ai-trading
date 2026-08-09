"use client";

import React from "react";

export default function KubernetesClustersPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Kubernetes Cluster & HPA</h1>
        <p className="text-gray-400 mt-1">Horizontal Pod Autoscalers (HPA) and stateful pod replicas.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h2 className="text-xl font-bold text-white mb-4">Autoscaling Policies (HPA)</h2>
        <div className="space-y-3">
          <div className="bg-black/50 border border-gray-800 p-4 rounded-lg flex justify-between items-center">
            <div>
              <span className="font-bold text-white">hpa-trading-service</span>
              <p className="text-xs text-gray-400">Target CPU: 75% | Min: 2 | Max: 20 Replicas</p>
            </div>
            <span className="text-xs bg-emerald-950 text-emerald-300 px-3 py-1 rounded border border-emerald-700">2 REPLICAS ACTIVE</span>
          </div>
        </div>
      </div>
    </div>
  );
}
