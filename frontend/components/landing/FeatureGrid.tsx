"use client";

import React from "react";

export default function FeatureGrid() {
  const features = [
    {
      title: "AI Signal Engine",
      description: "AutoML XGBoost & LSTM ensembles delivering real-time direction and confidence signals."
    },
    {
      title: "Portfolio Optimization",
      description: "Mean-Variance, Equal Risk Contribution (ERC) Risk Parity, and Black-Litterman Bayesian allocation."
    },
    {
      title: "Smart Order Router (SOR)",
      description: "Policy-based venue selection across Binance, Bybit, OKX, Kraken, and Coinbase."
    },
    {
      title: "Institutional Risk Controls",
      description: "7 real-time circuit breakers including daily loss limits, VaR (99%), and max drawdown caps."
    },
    {
      title: "MLOps & Autonomous Retraining",
      description: "Population Stability Index (PSI) drift detection, shadow deployments, and canary rollouts."
    },
    {
      title: "High Availability Observability",
      description: "Prometheus exporter, Grafana dashboards, OpenTelemetry tracing, and Kubernetes HPA."
    }
  ];

  return (
    <section className="py-20 bg-black border-b border-gray-800/60">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <h2 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
            Institutional-Grade Capabilities Built for Scale
          </h2>
          <p className="text-gray-400 text-base">
            From single-bot trading to multi-strategy enterprise quantitative asset management.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((f, idx) => (
            <div key={idx} className="bg-gray-950 border border-gray-800/80 p-6 rounded-2xl hover:border-indigo-600/50 transition-colors group">
              <div className="w-10 h-10 rounded-xl bg-indigo-950 text-indigo-400 flex items-center justify-center font-bold text-lg mb-4 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                {idx + 1}
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{f.title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{f.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
