"use client";

import React from "react";

export default function PlatformClustersPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Multi-Region Kubernetes Clusters</h1>
        <p className="text-gray-400 mt-1">Active-Active global cluster topology, HPA/VPA autoscaling, & Istio service mesh.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl space-y-2">
          <div className="flex justify-between items-center">
            <span className="font-mono text-xs text-indigo-400 font-bold">K8S-PROD-US-EAST-1</span>
            <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">HEALTHY</span>
          </div>
          <h3 className="text-lg font-bold text-white mt-1">Primary East Cluster</h3>
          <p className="text-xs text-gray-400">Replicas: 3-10 HPA | Istio mTLS: STRICT | Nodes: 12</p>
        </div>

        <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl space-y-2">
          <div className="flex justify-between items-center">
            <span className="font-mono text-xs text-indigo-400 font-bold">K8S-PROD-US-WEST-2</span>
            <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">HEALTHY</span>
          </div>
          <h3 className="text-lg font-bold text-white mt-1">Secondary West Cluster</h3>
          <p className="text-xs text-gray-400">Replicas: 3-10 HPA | Istio mTLS: STRICT | Nodes: 12</p>
        </div>
      </div>
    </div>
  );
}
