"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { ManualOrderForm } from "@/components/orders/ManualOrderForm";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery } from "@tanstack/react-query";
import { fetchPortfolio, fetchMarketSummary, fetchNewsSentiment, submitOrder, toggleBot, setStrategy } from "@/services/api";
import { Coins } from "lucide-react";

const SUPPORTED_SYMBOLS = [
  "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT", "DOGE/USDT", "AVAX/USDT", "DOT/USDT", "LINK/USDT",
  "MATIC/USDT", "ATOM/USDT", "NEAR/USDT", "APT/USDT", "SUI/USDT", "OP/USDT", "ARB/USDT", "LTC/USDT", "ETC/USDT", "XLM/USDT",
  "FIL/USDT", "INJ/USDT", "TIA/USDT", "UNI/USDT", "ICP/USDT", "FET/USDT", "RNDR/USDT", "PEPE/USDT", "SHIB/USDT", "FLOKI/USDT",
  "AAVE/USDT", "MKR/USDT", "SNX/USDT", "CRV/USDT", "LDO/USDT", "GRT/USDT", "ALGO/USDT", "FTM/USDT", "SAND/USDT", "MANA/USDT",
  "THETA/USDT", "AXS/USDT", "EGLD/USDT", "EOS/USDT", "FLOW/USDT", "KAVA/USDT", "MINA/USDT", "QNT/USDT", "RUNE/USDT", "WOO/USDT"
];

export default function OrdersPage() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [symbol, setSymbol] = useState("BTC/USDT");
  const stream = useTradingStream();

  const portfolioQuery = useQuery({ queryKey: ["portfolio"], queryFn: fetchPortfolio, refetchInterval: 5000 });
  const marketQuery = useQuery({ queryKey: ["market-summary", symbol, "1h"], queryFn: () => fetchMarketSummary(symbol, "1h"), refetchInterval: 10000 });
  const newsQuery = useQuery({ queryKey: ["news-sentiment"], queryFn: fetchNewsSentiment, refetchInterval: 300000 });

  const currentPortfolio = stream.portfolio ?? portfolioQuery.data ?? null;
  const currentPrice = stream.isConnected ? stream.livePrices[symbol] ?? marketQuery.data?.current_price ?? null : marketQuery.data?.current_price ?? null;

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500/30">
      <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} connectionState={stream.connectionState} />
      <div className={`flex-1 min-w-0 p-4 transition-all duration-300 lg:p-6 ${sidebarCollapsed ? "ml-20" : "ml-64"}`}>
        <Header portfolio={currentPortfolio} newsSentiment={newsQuery.data ?? null} latency={stream.latency} connectionState={stream.connectionState} onToggleBot={(enable) => toggleBot(enable)} onSelectStrategy={(s) => setStrategy(s)} />
        <main className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <h1 className="text-xl font-bold tracking-tight text-slate-100">Manual Order Execution Terminal</h1>
            <div className="flex items-center gap-2">
              <Coins className="h-4 w-4 text-cyan-400" />
              <span className="text-xs font-semibold text-slate-400">Asset:</span>
              <select
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                className="bg-slate-900 border border-slate-700 text-cyan-300 text-xs font-bold rounded-xl px-3 py-1.5 focus:outline-none focus:border-cyan-500"
              >
                {SUPPORTED_SYMBOLS.map((s) => (
                  <option key={s} value={s} className="bg-slate-900 text-slate-100 font-semibold">
                    {s}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="max-w-xl">
            <ManualOrderForm
              symbol={symbol}
              currentPrice={currentPrice}
              onSubmitOrder={async (side, alloc, lev, type) => {
                await submitOrder({ symbol, side, order_type: type, allocation_usd: alloc, leverage: lev });
                portfolioQuery.refetch();
              }}
            />
          </div>
        </main>
        <Footer dbSyncStatus={currentPortfolio?.database_sync_status} lastValidationTime={currentPortfolio?.last_validation_time} connectionState={stream.connectionState} />
      </div>
    </div>
  );
}
