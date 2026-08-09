"use client";

import React from "react";
import Link from "next/link";

export default function PricingCards() {
  const plans = [
    {
      name: "Free Simulator",
      price: "$0",
      period: "/ month",
      desc: "For paper trading and quantitative backtesting",
      features: ["10,000 API requests / mo", "1 Team Seat", "Paper Trading Simulator", "Basic Analytics"],
      buttonText: "Start Free",
      buttonHref: "/register",
      highlighted: false
    },
    {
      name: "Pro Trader",
      price: "$199",
      period: "/ month",
      desc: "For active quantitative traders & small funds",
      features: ["100,000 API requests / mo", "5 Team Seats", "Live Exchange SOR Integration", "MLOps & Drift Detection"],
      buttonText: "Upgrade to Pro",
      buttonHref: "/register",
      highlighted: true
    },
    {
      name: "Institutional Enterprise",
      price: "$999",
      period: "/ month",
      desc: "For quantitative hedge funds & asset managers",
      features: ["1,000,000 API requests / mo", "25 Team Seats", "Dedicated K8s Cluster & SLA", "AI Governance & Audit Trail"],
      buttonText: "Contact Enterprise",
      buttonHref: "/contact",
      highlighted: false
    }
  ];

  return (
    <section className="py-20 bg-gray-950 border-b border-gray-800/60" id="pricing">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <h2 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">Simple, Transparent Subscription Pricing</h2>
          <p className="text-gray-400">Scale seamlessly from paper simulation to institutional live exchange execution.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((p, idx) => (
            <div key={idx} className={`bg-gray-900 border rounded-2xl p-8 flex flex-col justify-between relative ${p.highlighted ? "border-indigo-500 shadow-2xl shadow-indigo-600/20" : "border-gray-800"}`}>
              {p.highlighted && (
                <span className="bg-indigo-600 text-white text-xs font-bold px-3 py-1 rounded-full absolute -top-3 right-6">
                  MOST POPULAR
                </span>
              )}
              <div>
                <h3 className="text-xl font-bold text-white">{p.name}</h3>
                <p className="text-xs text-gray-400 mt-1 mb-4">{p.desc}</p>
                <div className="text-4xl font-extrabold text-white">
                  {p.price} <span className="text-sm font-normal text-gray-400">{p.period}</span>
                </div>

                <ul className="space-y-3 text-sm text-gray-300 my-8">
                  {p.features.map((f, fIdx) => (
                    <li key={fIdx} className="flex items-center gap-2">
                      <span className="text-emerald-400 font-bold">✓</span> {f}
                    </li>
                  ))}
                </ul>
              </div>

              <Link href={p.buttonHref} className={`w-full py-3 rounded-xl text-center font-bold text-sm transition-all ${p.highlighted ? "bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg" : "bg-gray-800 hover:bg-gray-700 text-white"}`}>
                {p.buttonText}
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
