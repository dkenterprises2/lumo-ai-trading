"use client";

import React, { useState } from "react";
import { PortfolioState } from "@/types/trading";
import { ActivePositionsTable } from "@/components/positions/ActivePositionsTable";
import { TradeHistoryTable } from "@/components/history/TradeHistoryTable";
import { WalletLedgerTable } from "@/components/ledger/WalletLedgerTable";
import { PnlEquityChart } from "@/components/charts/PnlEquityChart";
import { Crosshair, ClipboardList, History, BookOpen, TrendingUp } from "lucide-react";

interface BottomTabsPanelProps {
  portfolio: PortfolioState | null;
  onPositionAction: (symbol: string, action: "CLOSE" | "PARTIAL_CLOSE" | "REVERSE") => void;
}

export function BottomTabsPanel({ portfolio, onPositionAction }: BottomTabsPanelProps) {
  const [activeTab, setActiveTab] = useState<"positions" | "orders" | "trades" | "ledger" | "pnl">("positions");

  const openPositions = portfolio?.active_positions || [];
  const openOrders = portfolio?.open_orders || [];
  const tradeHistory = portfolio?.trade_history || [];
  const walletLedger = portfolio?.ledger || [];
  const pnlHistory = portfolio?.pnl_history || [];

  return (
    <div className="rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl overflow-hidden">
      {/* Navigation Tabs Bar */}
      <div className="flex items-center gap-2 px-4 pt-3 border-b border-slate-800/80 bg-slate-950/80 overflow-x-auto scrollbar-none">
        <button
          onClick={() => setActiveTab("positions")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-t-xl text-xs font-bold transition border-b-2 ${
            activeTab === "positions"
              ? "bg-slate-900 text-cyan-400 border-cyan-400"
              : "text-slate-400 hover:text-slate-200 border-transparent"
          }`}
        >
          <Crosshair className="h-4 w-4" />
          <span>Open Positions ({openPositions.length})</span>
        </button>

        <button
          onClick={() => setActiveTab("orders")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-t-xl text-xs font-bold transition border-b-2 ${
            activeTab === "orders"
              ? "bg-slate-900 text-cyan-400 border-cyan-400"
              : "text-slate-400 hover:text-slate-200 border-transparent"
          }`}
        >
          <ClipboardList className="h-4 w-4" />
          <span>Open Orders ({openOrders.length})</span>
        </button>

        <button
          onClick={() => setActiveTab("trades")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-t-xl text-xs font-bold transition border-b-2 ${
            activeTab === "trades"
              ? "bg-slate-900 text-cyan-400 border-cyan-400"
              : "text-slate-400 hover:text-slate-200 border-transparent"
          }`}
        >
          <History className="h-4 w-4" />
          <span>Trade History ({tradeHistory.length})</span>
        </button>

        <button
          onClick={() => setActiveTab("ledger")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-t-xl text-xs font-bold transition border-b-2 ${
            activeTab === "ledger"
              ? "bg-slate-900 text-cyan-400 border-cyan-400"
              : "text-slate-400 hover:text-slate-200 border-transparent"
          }`}
        >
          <BookOpen className="h-4 w-4" />
          <span>Wallet Ledger ({walletLedger.length})</span>
        </button>

        <button
          onClick={() => setActiveTab("pnl")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-t-xl text-xs font-bold transition border-b-2 ${
            activeTab === "pnl"
              ? "bg-slate-900 text-cyan-400 border-cyan-400"
              : "text-slate-400 hover:text-slate-200 border-transparent"
          }`}
        >
          <TrendingUp className="h-4 w-4" />
          <span>PnL History ({pnlHistory.length})</span>
        </button>
      </div>

      {/* Tab Contents */}
      <div className="p-4">
        {activeTab === "positions" && (
          <ActivePositionsTable positions={openPositions} onAction={onPositionAction} />
        )}

        {activeTab === "orders" && (
          <div className="p-8 text-center text-xs text-slate-500 font-mono">
            {openOrders.length === 0 ? "No active limit/pending orders." : JSON.stringify(openOrders)}
          </div>
        )}

        {activeTab === "trades" && (
          <TradeHistoryTable trades={tradeHistory} />
        )}

        {activeTab === "ledger" && (
          <WalletLedgerTable ledger={walletLedger} />
        )}

        {activeTab === "pnl" && (
          <PnlEquityChart pnlHistory={pnlHistory} />
        )}
      </div>
    </div>
  );
}
