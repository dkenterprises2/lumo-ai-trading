"use client";

import React, { useState } from "react";

export default function FaqSection() {
  const faqs = [
    {
      q: "Does Lumo support paper trading?",
      a: "Yes! Lumo includes a full-featured paper trading simulator to test strategies and portfolio allocations with zero financial risk."
    },
    {
      q: "Which exchanges are supported for live trading?",
      a: "Lumo supports Binance (Spot & Futures), Bybit (Spot & Perpetual), OKX (Spot & Swap), Kraken, and Coinbase."
    },
    {
      q: "How does the Emergency Kill Switch work?",
      a: "The Emergency Kill Switch provides one-click instant cancellation of all open live orders and halts new order submissions across connected exchanges."
    },
    {
      q: "Is my API key data secure?",
      a: "API keys are encrypted using AES-256 and stored with SHA-256 secret hashes. Lumo never requests withdrawal permissions on exchange keys."
    }
  ];

  return (
    <section className="py-20 bg-black border-b border-gray-800/60" id="faq">
      <div className="max-w-4xl mx-auto px-6">
        <div className="text-center mb-16 space-y-4">
          <h2 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">Frequently Asked Questions</h2>
          <p className="text-gray-400">Everything you need to know about the Lumo AI Trading Platform.</p>
        </div>

        <div className="space-y-4">
          {faqs.map((f, idx) => (
            <div key={idx} className="bg-gray-950 border border-gray-800 p-6 rounded-2xl">
              <h3 className="text-lg font-bold text-white mb-2">{f.q}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{f.a}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
