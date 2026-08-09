"use client";

import React from "react";

export default function TradingShowcase() {
  return (
    <section className="py-20 bg-black border-b border-gray-800/60">
      <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
        <div className="space-y-6">
          <span className="text-xs font-bold text-indigo-400 uppercase tracking-widest">Multi-Exchange Order Routing</span>
          <h2 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
            Smart Order Router (SOR) & Execution Reconciliation
          </h2>
          <p className="text-gray-400 text-base leading-relaxed">
            Eliminate price slippage and manual order routing. Lumo's SOR evaluates liquidity depth, fee tiers, and latency across top crypto exchanges in real time.
          </p>
          <ul className="space-y-3 text-sm text-gray-300">
            <li className="flex items-center gap-2">
              <span className="text-emerald-400 font-bold">✓</span> 6 Routing Policies: Best Price, Lowest Fee, High Liquidity, Low Slippage
            </li>
            <li className="flex items-center gap-2">
              <span className="text-emerald-400 font-bold">✓</span> Partial fill detection & orderbook state reconciliation
            </li>
            <li className="flex items-center gap-2">
              <span className="text-emerald-400 font-bold">✓</span> Emergency Kill Switch for instantaneous risk halt
            </li>
          </ul>
        </div>

        <div className="bg-gray-950 border border-gray-800 p-6 rounded-2xl space-y-4">
          <div className="text-sm text-gray-400 font-semibold mb-2">Live Execution Routing Log</div>
          <div className="bg-black p-4 rounded-xl font-mono text-xs text-gray-300 space-y-2">
            <div className="text-emerald-400">[SOR] Order BTC/USDT 0.05 Routed to BINANCE_SPOT</div>
            <div className="text-gray-400">Fill Price: $64,800.00 | Fee: $0.32 | Slippage: +2.3 bps</div>
            <div className="text-indigo-400">[RECONCILIATION] Audit Matched — State: FILLED</div>
          </div>
        </div>
      </div>
    </section>
  );
}
