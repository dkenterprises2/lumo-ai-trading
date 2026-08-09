"use client";

import React from "react";
import Link from "next/link";

export default function CloudNativePlatformOverviewPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Cloud-Native Kubernetes, DevSecOps & SRE Hub</h1>
        <p className="text-gray-400 mt-1">Multi-cluster topology, ArgoCD GitOps, Istio zero-trust mesh, OpenTelemetry, & Chaos Engineering.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Link href="/platform/clusters" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Active Clusters</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">2 Active-Active</div>
          <div className="text-xs text-gray-500 mt-1">us-east-1 & us-west-2</div>
        </Link>

        <Link href="/platform/gitops" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">GitOps Delivery</div>
          <div className="text-2xl font-bold text-indigo-400 mt-1">ArgoCD SYNCED</div>
          <div className="text-xs text-gray-500 mt-1">Zero Drift Detected</div>
        </Link>

        <Link href="/platform/sre" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">SRE Error Budget</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">99.98% SLO</div>
          <div className="text-xs text-emerald-400 mt-1">82% Budget Remaining</div>
        </Link>

        <Link href="/platform/chaos" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Chaos Experiments</div>
          <div className="text-2xl font-bold text-white mt-1">PASSED</div>
          <div className="text-xs text-gray-500 mt-1">Pod Termination Blast Test</div>
        </Link>
      </div>
    </div>
  );
}
