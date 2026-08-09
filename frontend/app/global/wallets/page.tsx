"use client";

import React from "react";

export default function CrossChainWalletsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Cross-Chain Wallet Intelligence</h1>
        <p className="text-gray-400 mt-1">Multi-chain self-custody & treasury wallet balance aggregator.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">ETHEREUM (TREASURY_MAIN)</span>
            <h3 className="text-base font-semibold text-white mt-1">0x71C7656EC7ab88b098defB751B7401B5f6d8976F</h3>
            <p className="text-xs text-gray-400">Balance: $1,250,000.00 USD</p>
          </div>
          <span className="text-xs bg-indigo-950 text-indigo-300 border border-indigo-700 px-3 py-1 rounded">ETH MAINNET</span>
        </div>
      </div>
    </div>
  );
}
