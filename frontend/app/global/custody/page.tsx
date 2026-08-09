"use client";

import React from "react";

export default function CustodyPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Custody & Institutional Vault Management</h1>
        <p className="text-gray-400 mt-1">Multi-custodian vault distribution across Fireblocks, BitGo, & Cold Storage.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800 flex justify-between items-center">
            <div>
              <span className="text-xs text-indigo-400 font-bold font-mono">FIREBLOCKS MPC VAULT</span>
              <h3 className="text-lg font-bold text-white mt-1">$3,200,000.00 USD</h3>
              <p className="text-xs text-gray-400">Account Type: MPC_VAULT</p>
            </div>
            <span className="text-xs bg-indigo-950 text-indigo-300 border border-indigo-700 px-3 py-1 rounded">MPC VAULT</span>
          </div>

          <div className="bg-black/50 p-4 rounded-lg border border-gray-800 flex justify-between items-center">
            <div>
              <span className="text-xs text-emerald-400 font-bold font-mono">BITGO COLD STORAGE</span>
              <h3 className="text-lg font-bold text-white mt-1">$1,800,000.00 USD</h3>
              <p className="text-xs text-gray-400">Account Type: COLD_STORAGE</p>
            </div>
            <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">COLD STORAGE</span>
          </div>
        </div>
      </div>
    </div>
  );
}
