"use client";

import React from "react";
import { WalletTransaction } from "@/types/trading";
import { BookOpen } from "lucide-react";

interface WalletLedgerTableProps {
  ledger: WalletTransaction[];
}

export function WalletLedgerTable({ ledger }: WalletLedgerTableProps) {
  const reversedLedger = (ledger || []).slice().reverse();

  return (
    <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-teal-500/10 text-teal-400">
            <BookOpen className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-bold text-slate-100 text-base">Wallet Ledger (Double-Entry Log)</h3>
            <p className="text-xs text-slate-400">Complete Reconstructable Balance History</p>
          </div>
        </div>

        <span className="text-xs font-semibold px-2.5 py-1 rounded-xl bg-teal-500/10 text-teal-400 border border-teal-500/20">
          {ledger ? ledger.length : 0} Ledger Entries
        </span>
      </div>

      <div className="overflow-x-auto max-h-72 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-800">
        <table className="w-full text-left text-xs">
          <thead className="sticky top-0 bg-slate-950/90 backdrop-blur-md text-slate-400 border-b border-slate-800">
            <tr>
              <th className="py-2.5 px-3 font-semibold">Tx ID</th>
              <th className="py-2.5 px-3 font-semibold">Timestamp</th>
              <th className="py-2.5 px-3 font-semibold">Type</th>
              <th className="py-2.5 px-3 font-semibold">Amount</th>
              <th className="py-2.5 px-3 font-semibold">Balance After</th>
              <th className="py-2.5 px-3 font-semibold text-right">Description / Ref</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-200 font-medium">
            {(!reversedLedger || reversedLedger.length === 0) ? (
              <tr>
                <td colSpan={6} className="py-8 text-center text-slate-500">
                  No transaction ledger records.
                </td>
              </tr>
            ) : (
              reversedLedger.map((tx) => {
                const isCredit = tx.amount >= 0;
                const amtSign = isCredit ? "+" : "";

                return (
                  <tr key={tx.tx_id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-3 font-mono font-bold text-slate-200">{tx.tx_id}</td>
                    <td className="py-3 px-3 font-mono text-slate-400">{tx.timestamp}</td>
                    <td className="py-3 px-3">
                      <span
                        className={`px-2 py-0.5 rounded-md text-[10px] font-bold ${
                          isCredit
                            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                            : "bg-rose-500/10 text-rose-400 border border-rose-500/30"
                        }`}
                      >
                        {tx.tx_type}
                      </span>
                    </td>
                    <td className={`py-3 px-3 font-mono font-bold ${isCredit ? "text-emerald-400" : "text-rose-400"}`}>
                      {amtSign}${tx.amount.toFixed(2)}
                    </td>
                    <td className="py-3 px-3 font-mono font-bold text-slate-100">${tx.balance_after.toFixed(2)}</td>
                    <td className="py-3 px-3 text-right text-slate-400">{tx.description || tx.reference_id}</td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
