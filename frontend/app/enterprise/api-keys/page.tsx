"use client";

import React from "react";

export default function EnterpriseAPIKeysPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">API Key Management & Scopes</h1>
        <p className="text-gray-400 mt-1">Scoped API keys, key rotation, expiration policies, & secret management.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-emerald-400 font-bold">KEY_LIVE_991</span>
            <h3 className="text-base font-semibold text-white mt-1">Production Trading Bot (lumo_live_x88...)</h3>
            <p className="text-xs text-gray-400">Scopes: marketdata:read, execution:write, ai:manage</p>
          </div>
          <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1 rounded text-xs font-bold">Rotate Key</button>
        </div>
      </div>
    </div>
  );
}
