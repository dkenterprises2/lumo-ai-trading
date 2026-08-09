"use client";

import React from "react";
import Link from "next/link";

export default function GlobalMultiAssetOverviewPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Global Multi-Asset & Prime Brokerage Platform</h1>
        <p className="text-gray-400 mt-1">Unified portfolio NAV across Crypto, Equities, Futures, Options, Forex, DeFi & Prime Brokers.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Link href="/global/unified-portfolio" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Global Unified NAV</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">$2,950,000.00</div>
          <div className="text-xs text-gray-500 mt-1">CeFi ($2.1M) + DeFi ($850K)</div>
        </Link>

        <Link href="/global/brokers" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Prime Brokerage</div>
          <div className="text-2xl font-bold text-indigo-400 mt-1">2 Prime Brokers</div>
          <div className="text-xs text-gray-500 mt-1">Goldman Sachs & Coinbase Prime</div>
        </Link>

        <Link href="/global/arbitrage" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Cross-Chain Arbitrage</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">9.3 bps Net Spread</div>
          <div className="text-xs text-emerald-400 mt-1">PROFITABLE GRAPH ROUTE</div>
        </Link>

        <Link href="/global/treasury" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Treasury & Yield</div>
          <div className="text-2xl font-bold text-white mt-1">$5,000,000.00</div>
          <div className="text-xs text-emerald-400 mt-1">5.45% Avg Yield APY</div>
        </Link>
      </div>
    </div>
  );
}
