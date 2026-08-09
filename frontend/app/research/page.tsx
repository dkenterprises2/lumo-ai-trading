"use client";

import React from "react";
import Link from "next/link";

export default function EnterpriseQuantResearchPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Enterprise Quant Research Platform</h1>
        <p className="text-gray-400 mt-1">Parquet Data Lake, DuckDB analytics, Feature Store, Experiment Tracking, & Alpha Discovery.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Link href="/research/data-lake" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Data Lake Storage</div>
          <div className="text-2xl font-bold text-indigo-400 mt-1">1.45 TB ZSTD</div>
          <div className="text-xs text-gray-500 mt-1">1,420 Parquet Partitions</div>
        </Link>

        <Link href="/research/features" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Feature Registry</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">24 Features</div>
          <div className="text-xs text-gray-500 mt-1">Online/Offline Parity</div>
        </Link>

        <Link href="/research/experiments" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Active Experiments</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">Sharpe: 2.45</div>
          <div className="text-xs text-gray-500 mt-1">StatArb Pair Sweep</div>
        </Link>

        <Link href="/research/alpha-lab" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Alpha Candidates</div>
          <div className="text-2xl font-bold text-white mt-1">2 Approved</div>
          <div className="text-xs text-emerald-400 mt-1">Shadow Testing Ready</div>
        </Link>
      </div>
    </div>
  );
}
