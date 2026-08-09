"use client";

import React from "react";

export default function HowItWorks() {
  const steps = [
    { step: "01", title: "Connect Exchange Accounts", desc: "Link Binance, Bybit, or OKX API keys securely with read/trade permissions." },
    { step: "02", title: "Select AI Trading Models", desc: "Choose from pre-trained trend, mean-reversion, or RL quantitative strategies." },
    { step: "03", title: "Configure Portfolio & Risk Caps", desc: "Set max daily loss limits, fractional Kelly position sizes, and target volatility." },
    { step: "04", title: "Deploy Autonomous Execution", desc: "Smart Order Router places and reconciles orders with real-time slippage tracking." }
  ];

  return (
    <section className="py-20 bg-gray-950 border-b border-gray-800/60">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <h2 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">How Lumo AI Works</h2>
          <p className="text-gray-400">Deploy quantitative AI strategies in under 5 minutes.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {steps.map((s, idx) => (
            <div key={idx} className="bg-black/60 border border-gray-800 p-6 rounded-2xl relative">
              <span className="text-4xl font-extrabold text-indigo-900/60 mb-2 block">{s.step}</span>
              <h3 className="text-lg font-bold text-white mb-2">{s.title}</h3>
              <p className="text-xs text-gray-400 leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
