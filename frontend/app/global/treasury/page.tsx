"use client";

import React from "react";

export default function TreasuryPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Treasury & Stablecoin Yield Management</h1>
        <p className="text-gray-400 mt-1">Idle cash laddering, yield venue ranking, & counterparty concentration limits.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Total Treasury Reserve</span>
            <div className="text-2xl font-bold text-white mt-1">$5,000,000.00</div>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Staked Yield Value</span>
            <div className="text-2xl font-bold text-emerald-400 mt-1">$3,000,000.00</div>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Weighted APY</span>
            <div className="text-2xl font-bold text-indigo-400 mt-1">5.45% APY</div>
          </div>
        </div>
      </div>
    </div>
  );
}
