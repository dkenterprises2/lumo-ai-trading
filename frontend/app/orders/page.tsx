"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { ManualOrderForm } from "@/components/orders/ManualOrderForm";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery } from "@tanstack/react-query";
import { fetchPortfolio, fetchMarketSummary, fetchNewsSentiment, submitOrder, toggleBot, setStrategy } from "@/services/api";

export default function OrdersPage() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [symbol] = useState("BTC/USDT");
  const stream = useTradingStream();

  const portfolioQuery = useQuery({ queryKey: ["portfolio"], queryFn: fetchPortfolio, refetchInterval: 5000 });
  const marketQuery = useQuery({ queryKey: ["market-summary", symbol, "1h"], queryFn: () => fetchMarketSummary(symbol, "1h"), refetchInterval: 10000 });
  const newsQuery = useQuery({ queryKey: ["news-sentiment"], queryFn: fetchNewsSentiment, refetchInterval: 300000 });

  const currentPortfolio = stream.isConnected && stream.portfolio ? stream.portfolio : portfolioQuery.data ?? null;
  const currentPrice = stream.isConnected ? stream.livePrices[symbol] ?? marketQuery.data?.current_price ?? null : marketQuery.data?.current_price ?? null;

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500/30">
      <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} connectionState={stream.connectionState} />
      <div className={`flex-1 min-w-0 p-4 transition-all duration-300 lg:p-6 ${sidebarCollapsed ? "ml-20" : "ml-64"}`}>
        <Header portfolio={currentPortfolio} newsSentiment={newsQuery.data ?? null} latency={stream.latency} connectionState={stream.connectionState} onToggleBot={(enable) => toggleBot(enable)} onSelectStrategy={(s) => setStrategy(s)} />
        <main className="space-y-6">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold tracking-tight text-slate-100">Manual Order Execution Terminal</h1>
          </div>
          <div className="max-w-xl">
            <ManualOrderForm symbol={symbol} currentPrice={currentPrice} onSubmitOrder={(side, alloc, lev, type) => submitOrder({ symbol, side, order_type: type, allocation_usd: alloc, leverage: lev })} />
          </div>
        </main>
        <Footer dbSyncStatus={currentPortfolio?.database_sync_status} lastValidationTime={currentPortfolio?.last_validation_time} connectionState={stream.connectionState} />
      </div>
    </div>
  );
}
