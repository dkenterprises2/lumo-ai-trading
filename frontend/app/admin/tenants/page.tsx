"use client";

import React from "react";

export default function AdminTenantsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Tenant Management Console</h1>
        <p className="text-gray-400 mt-1">Global organization activation, suspension, and tenant isolation control.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-400">
            <thead className="bg-black/50 text-gray-300 uppercase text-xs">
              <tr>
                <th className="px-4 py-3">Tenant ID</th>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Slug</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-gray-800">
                <td className="px-4 py-3 font-mono text-white">ORG-101</td>
                <td className="px-4 py-3 text-white font-semibold">Alpha Quant Capital</td>
                <td className="px-4 py-3 font-mono">alpha-quant</td>
                <td className="px-4 py-3 text-emerald-400 font-bold">ACTIVE</td>
                <td className="px-4 py-3">
                  <button className="text-xs bg-red-950 text-red-400 border border-red-800 px-3 py-1 rounded">Suspend</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
