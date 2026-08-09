"use client";

import React from "react";

export default function BasketOrdersPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Basket Order Execution & Rebalancing</h1>
        <p className="text-gray-400 mt-1">Multi-asset basket routing, index tracking rebalances, & portfolio allocations.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">BASKET_ID: BSK_101</span>
            <h3 className="text-lg font-bold text-white mt-1">Crypto Top 5 Market-Cap Rebalance Basket</h3>
            <p className="text-xs text-gray-400">Total Notional: $1,250,000 | Components: 5 Instruments</p>
          </div>
          <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1 rounded text-xs font-bold">Route Basket</button>
        </div>
      </div>
    </div>
  );
}
