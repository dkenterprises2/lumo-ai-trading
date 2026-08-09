"use client";

import React from "react";

export default function FactorResearchPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Factor Research & Alpha Library</h1>
        <p className="text-gray-400 mt-1">Formulaic alphas, Information Coefficient (IC) evaluation, and factor correlation heatmaps.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-400">
            <thead className="bg-black/50 text-gray-300 uppercase text-xs">
              <tr>
                <th className="px-4 py-3">Alpha ID</th>
                <th className="px-4 py-3">Factor Name</th>
                <th className="px-4 py-3">Category</th>
                <th className="px-4 py-3">Information Coefficient (IC)</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-gray-800">
                <td className="px-4 py-3 font-mono text-indigo-400 font-bold">ALPHA-001</td>
                <td className="px-4 py-3 font-bold text-white">CrossSectionalMomentum</td>
                <td className="px-4 py-3">MOMENTUM</td>
                <td className="px-4 py-3 text-emerald-400 font-bold">0.084</td>
              </tr>
              <tr className="border-b border-gray-800">
                <td className="px-4 py-3 font-mono text-indigo-400 font-bold">ALPHA-002</td>
                <td className="px-4 py-3 font-bold text-white">MeanReversionZScore</td>
                <td className="px-4 py-3">VALUE</td>
                <td className="px-4 py-3 text-emerald-400 font-bold">0.062</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
