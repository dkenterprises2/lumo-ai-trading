"use client";

import React from "react";

export default function AutonomousAlphaFactoryPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Autonomous Alpha Discovery Factory</h1>
        <p className="text-gray-400 mt-1">Continuous discovery, evolution, validation, governance approval, & retirement loop.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl space-y-1">
          <span className="text-xs text-gray-400 font-medium">AutoML Candidates</span>
          <div className="text-2xl font-bold text-indigo-400 mt-1">1,420 Generated</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl space-y-1">
          <span className="text-xs text-gray-400 font-medium">Genetic Generations</span>
          <div className="text-2xl font-bold text-emerald-400 mt-1">42 Generations</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl space-y-1">
          <span className="text-xs text-gray-400 font-medium">Certified Robust</span>
          <div className="text-2xl font-bold text-amber-400 mt-1">88% Robustness</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl space-y-1">
          <span className="text-xs text-gray-400 font-medium">Shadow Deployed</span>
          <div className="text-2xl font-bold text-white mt-1">2 Active Alphas</div>
        </div>
      </div>
    </div>
  );
}
