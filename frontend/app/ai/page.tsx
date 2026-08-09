"use client";

import React from "react";
import Link from "next/link";

export default function AutonomousAIOverviewPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Autonomous Multi-Agent AI Platform</h1>
        <p className="text-gray-400 mt-1">Reinforcement learning, regime specialists, portfolio allocators, & AI governance control tower.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Link href="/ai/agents" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Multi-Agent Fleet</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">4 Active Specialists</div>
          <div className="text-xs text-gray-500 mt-1">Trend, MeanRev, Mom, Volatility</div>
        </Link>

        <Link href="/ai/shadow-learning" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Shadow Learning</div>
          <div className="text-2xl font-bold text-indigo-400 mt-1">Paper-Trading Mode</div>
          <div className="text-xs text-gray-500 mt-1">Counterfactual PnL: +$125.40</div>
        </Link>

        <Link href="/ai/governance" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">AI Governance</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">PPO_BULL_V1</div>
          <div className="text-xs text-emerald-400 mt-1">APPROVED (Sharpe: 2.45)</div>
        </Link>

        <Link href="/ai/kill-switch" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">AI Kill-Switch</div>
          <div className="text-2xl font-bold text-white mt-1">OPERATIONAL</div>
          <div className="text-xs text-gray-500 mt-1">Emergency Circuit Breaker Ready</div>
        </Link>
      </div>
    </div>
  );
}
