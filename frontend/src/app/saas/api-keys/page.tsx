"use client";

import React from "react";

export default function TenantAPIKeysPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">API Keys & Secret Rotation</h1>
        <p className="text-gray-400 mt-1">Tenant-scoped API key generation, HMAC authentication, and secret rotation.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-white">Active Tenant API Keys</h2>
          <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors">
            Generate New API Key
          </button>
        </div>

        <div className="space-y-3">
          <div className="border border-gray-800 rounded-lg p-4 bg-black/40 flex justify-between items-center">
            <div>
              <span className="font-mono text-xs text-indigo-400 font-bold">KEY-101</span>
              <h3 className="text-base font-semibold text-white mt-1">Production Trading Key</h3>
              <p className="font-mono text-xs text-gray-400">Prefix: lumo_pk_live...</p>
            </div>
            <button className="text-xs bg-red-950 text-red-400 border border-red-800 px-3 py-1 rounded">Revoke</button>
          </div>
        </div>
      </div>
    </div>
  );
}
