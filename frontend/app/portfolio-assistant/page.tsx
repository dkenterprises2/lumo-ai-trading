"use client";

import React from "react";

export default function ConversationalPortfolioAssistantPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Conversational Portfolio & Risk Assistant</h1>
        <p className="text-gray-400 mt-1">Explanations of factor contributions, VaR/CVaR narratives, & exposure drift.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl space-y-2">
          <span className="text-xs text-gray-400 font-medium">Portfolio Exposure Summary</span>
          <p className="text-sm text-gray-200">BTC exposure increased +4.2% due to momentum strategy execution. Portfolio VaR 3.1%.</p>
        </div>
        <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl space-y-2">
          <span className="text-xs text-gray-400 font-medium">Recommended Action</span>
          <p className="text-sm text-indigo-400 font-semibold">Reduce SOL concentration by 1.5% to maintain target volatility bounds.</p>
        </div>
      </div>
    </div>
  );
}
