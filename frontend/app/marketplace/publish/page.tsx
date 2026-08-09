"use client";

import React from "react";

export default function MarketplacePublishPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Strategy Publishing & Certification Submission</h1>
        <p className="text-gray-400 mt-1">Submit quant strategies for walk-forward robustness testing & marketplace listing.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Strategy Title</span>
            <div className="text-xl font-bold text-white mt-1">DOM Imbalance StatArb</div>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Certification Target</span>
            <div className="text-xl font-bold text-indigo-400 mt-1">INSTITUTIONAL CERTIFIED</div>
          </div>
        </div>
        <button className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded text-xs font-bold">Submit for Certification</button>
      </div>
    </div>
  );
}
