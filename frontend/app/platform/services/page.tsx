"use client";

import React from "react";

export default function MicroservicesRegistryPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Microservices Registry</h1>
        <p className="text-gray-400 mt-1">Real-time service discovery, heartbeat renewal, and round-robin load balancing.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-400">
            <thead className="bg-black/50 text-gray-300 uppercase text-xs">
              <tr>
                <th className="px-4 py-3">Service Name</th>
                <th className="px-4 py-3">Instance ID</th>
                <th className="px-4 py-3">Host:Port</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-gray-800">
                <td className="px-4 py-3 font-bold text-white">api-gateway</td>
                <td className="px-4 py-3 font-mono">api-gw-1</td>
                <td className="px-4 py-3 font-mono">10.0.1.10:8000</td>
                <td className="px-4 py-3 text-emerald-400 font-bold">UP</td>
              </tr>
              <tr className="border-b border-gray-800">
                <td className="px-4 py-3 font-bold text-white">trading-service</td>
                <td className="px-4 py-3 font-mono">trade-svc-1</td>
                <td className="px-4 py-3 font-mono">10.0.1.11:8001</td>
                <td className="px-4 py-3 text-emerald-400 font-bold">UP</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
