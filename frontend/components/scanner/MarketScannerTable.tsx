"use client";

import React from "react";
import { ScannerPair } from "@/types/trading";
import { Scan, TrendingUp, TrendingDown, Minus } from "lucide-react";

interface MarketScannerTableProps {
  scannerPairs: ScannerPair[];
  onSelectSymbol: (symbol: string) => void;
}

export function MarketScannerTable({ scannerPairs, onSelectSymbol }: MarketScannerTableProps) {
  return (
    <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-purple-500/10 text-purple-400">
            <Scan className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-bold text-slate-100 text-base">Multi-Symbol Market Scanner</h3>
            <p className="text-xs text-slate-400">14 Pairs Analyzed in Real-Time</p>
          </div>
        </div>

        <span className="text-xs font-semibold px-2.5 py-1 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
          {scannerPairs.length} Pairs Active
        </span>
      </div>

      <div className="overflow-x-auto max-h-72 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-800">
        <table className="w-full text-left text-xs">
          <thead className="sticky top-0 bg-slate-950/90 backdrop-blur-md text-slate-400 border-b border-slate-800">
            <tr>
              <th className="py-2.5 px-3 font-semibold">Symbol</th>
              <th className="py-2.5 px-3 font-semibold">Price</th>
              <th className="py-2.5 px-3 font-semibold">Action</th>
              <th className="py-2.5 px-3 font-semibold text-right">Confidence</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-200 font-medium">
            {scannerPairs.map((p) => {
              const isBuy = p.action.includes("BUY");
              const isSell = p.action.includes("SELL");

              return (
                <tr
                  key={p.symbol}
                  onClick={() => onSelectSymbol(p.symbol)}
                  className="hover:bg-slate-800/50 cursor-pointer transition-colors duration-150"
                >
                  <td className="py-2.5 px-3 font-bold text-slate-100">{p.symbol}</td>
                  <td className="py-2.5 px-3 font-mono">
                    ${p.current_price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 4 })}
                  </td>
                  <td className="py-2.5 px-3">
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-[10px] font-bold ${
                        isBuy
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                          : isSell
                          ? "bg-rose-500/10 text-rose-400 border border-rose-500/30"
                          : "bg-slate-800 text-slate-400 border border-slate-700"
                      }`}
                    >
                      {isBuy ? (
                        <TrendingUp className="h-3 w-3" />
                      ) : isSell ? (
                        <TrendingDown className="h-3 w-3" />
                      ) : (
                        <Minus className="h-3 w-3" />
                      )}
                      {p.action.replace("_", " ")}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-right font-bold text-cyan-400 font-mono">
                    {p.confidence_score}%
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
