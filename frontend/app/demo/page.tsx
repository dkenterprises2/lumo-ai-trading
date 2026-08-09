import React from "react";
import Navbar from "../../components/landing/Navbar";
import Footer from "../../components/landing/Footer";
import Link from "next/link";

export const metadata = {
  title: "Interactive Live Demo — Lumo AI Trading Platform",
  description: "Experience Lumo's AI signal engine, Smart Order Router, and risk controls in a live interactive simulator."
};

export default function DemoPage() {
  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />
      <div className="py-20 max-w-5xl mx-auto px-6 text-center space-y-8">
        <h1 className="text-4xl font-extrabold">Interactive Platform Demo</h1>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Explore Lumo's live trading dashboard, AI signal outputs, and portfolio optimization engines in interactive simulator mode.
        </p>

        <div className="bg-gray-950 border border-gray-800 p-8 rounded-2xl text-left space-y-6">
          <div className="flex justify-between items-center border-b border-gray-800 pb-4">
            <div>
              <h3 className="text-xl font-bold text-white">Paper Trading Simulator Mode</h3>
              <p className="text-xs text-gray-400">$100,000.00 Simulated Balance Initialized</p>
            </div>
            <Link href="/login" className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold px-6 py-2.5 rounded-lg text-sm transition-colors">
              Access Dashboard
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-black p-4 rounded-xl border border-gray-800">
              <div className="text-xs text-gray-400">Current Regime</div>
              <div className="text-lg font-bold text-emerald-400 mt-1">BULL_TREND (Confidence: 84.5%)</div>
            </div>
            <div className="bg-black p-4 rounded-xl border border-gray-800">
              <div className="text-xs text-gray-400">SOR Route</div>
              <div className="text-lg font-bold text-indigo-400 mt-1">BEST_PRICE (Binance Spot)</div>
            </div>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}
