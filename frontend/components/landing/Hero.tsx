"use client";

import React from "react";
import Link from "next/link";

export default function Hero() {
  return (
    <section className="relative overflow-hidden pt-20 pb-16 md:pt-32 md:pb-24 border-b border-gray-800/60 bg-gradient-to-b from-black via-gray-950 to-black">
      <div className="max-w-7xl mx-auto px-6 text-center space-y-8 relative z-10">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-950/60 border border-indigo-700/60 text-indigo-300 text-xs font-semibold uppercase tracking-wider">
          <span>🚀 Version 2.7 Released — Institutional AI Quantitative Engine</span>
        </div>

        <h1 className="text-4xl md:text-6xl font-extrabold text-white tracking-tight max-w-4xl mx-auto leading-tight">
          Lumo <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">AI Trading Platform</span>
        </h1>

        <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto font-normal">
          Autonomous Institutional Quantitative Trading for Crypto & Digital Assets. Advanced AI signal generation, Mean-Variance portfolio optimization, Smart Order Routing, and Institutional Risk Controls.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <Link href="/register" className="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-base px-8 py-3.5 rounded-xl transition-all shadow-xl shadow-indigo-600/30 hover:scale-105">
            Start Free
          </Link>
          <Link href="/demo" className="w-full sm:w-auto bg-gray-900 hover:bg-gray-800 border border-gray-700 text-gray-200 font-semibold text-base px-8 py-3.5 rounded-xl transition-all hover:text-white">
            View Live Demo
          </Link>
        </div>

        {/* Dashboard Preview Card */}
        <div className="pt-12 max-w-5xl mx-auto">
          <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-4 md:p-6 shadow-2xl backdrop-blur-xl">
            <div className="flex items-center gap-2 pb-4 border-b border-gray-800">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <div className="w-3 h-3 rounded-full bg-amber-500"></div>
              <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
              <span className="text-xs text-gray-500 font-mono ml-2">app.lumo.trade/dashboard</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 text-left">
              <div className="bg-black/50 border border-gray-800 p-4 rounded-xl">
                <div className="text-xs text-gray-400">Active Equity</div>
                <div className="text-2xl font-bold text-white mt-1">$148,250.00</div>
                <div className="text-xs text-emerald-400 mt-1">↑ +24.8% (30D)</div>
              </div>
              <div className="bg-black/50 border border-gray-800 p-4 rounded-xl">
                <div className="text-xs text-gray-400">Sharpe Ratio</div>
                <div className="text-2xl font-bold text-indigo-400 mt-1">2.84</div>
                <div className="text-xs text-gray-500 mt-1">Max Drawdown: 4.2%</div>
              </div>
              <div className="bg-black/50 border border-gray-800 p-4 rounded-xl">
                <div className="text-xs text-gray-400">SOR Execution Latency</div>
                <div className="text-2xl font-bold text-purple-400 mt-1">18.5 ms</div>
                <div className="text-xs text-emerald-400 mt-1">Binance / Bybit / OKX</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
