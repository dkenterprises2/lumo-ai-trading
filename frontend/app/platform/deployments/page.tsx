"use client";

import React from "react";

export default function MicroservicesDeploymentsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Deployment Rollout Console</h1>
        <p className="text-gray-400 mt-1">Docker Compose and Kubernetes zero-downtime rolling updates.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="space-y-3">
          <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
            <div>
              <span className="font-bold text-white">v2.8.0 Microservices Release</span>
              <p className="text-xs text-gray-400">Target Namespace: lumo-microservices</p>
            </div>
            <span className="text-xs bg-emerald-950 text-emerald-300 px-3 py-1 rounded border border-emerald-700">ROLLOUT COMPLETED</span>
          </div>
        </div>
      </div>
    </div>
  );
}
