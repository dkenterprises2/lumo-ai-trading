"use client";

import React, { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, CheckCircle2, RefreshCw } from "lucide-react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { TradingViewChart } from "@/components/charts/TradingViewChart";
import { RightOrderPanel } from "@/components/terminal/RightOrderPanel";
import { BottomTabsPanel } from "@/components/terminal/BottomTabsPanel";
import { MarketScannerTable } from "@/components/scanner/MarketScannerTable";
import { ManualOrderForm } from "@/components/orders/ManualOrderForm";
import { NewsSentimentPanel } from "@/components/news/NewsSentimentPanel";
import { useTradingStream } from "@/hooks/useTradingStream";
import {
  ApiError,
  fetchAiSignal,
  fetchMarketSummary,
  fetchNewsSentiment,
  fetchPortfolio,
  fetchScannerSummary,
  handlePositionAction,
  setStrategy,
  submitOrder,
  toggleBot
} from "@/services/api";

function messageFor(error: unknown) {
  return error instanceof ApiError || error instanceof Error
    ? error.message
    : "An unexpected dashboard error occurred.";
}

type ActionNotice = { tone: "success" | "error"; message: string } | null;

export default function DashboardPage() {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState("dashboard");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState("BTC/USDT");
  const [timeframe, setTimeframe] = useState("1h");
  const [actionNotice, setActionNotice] = useState<ActionNotice>(null);

  const stream = useTradingStream();
  const portfolioQuery = useQuery({
    queryKey: ["portfolio"],
    queryFn: fetchPortfolio,
    refetchInterval: stream.isConnected ? false : 5_000,
    retry: 2
  });

  const activeStrategy = portfolioQuery.data?.active_strategy ?? "AI Hybrid";
  const riskMode = portfolioQuery.data?.risk_mode ?? "Moderate";
  const marketQuery = useQuery({
    queryKey: ["market-summary", selectedSymbol, timeframe],
    queryFn: () => fetchMarketSummary(selectedSymbol, timeframe),
    refetchInterval: 10_000,
    retry: 2
  });
  const signalQuery = useQuery({
    queryKey: ["ai-signal", selectedSymbol, activeStrategy, riskMode],
    queryFn: () => fetchAiSignal(selectedSymbol, activeStrategy, riskMode),
    refetchInterval: 15_000,
    retry: 2
  });
  const newsQuery = useQuery({
    queryKey: ["news-sentiment"],
    queryFn: fetchNewsSentiment,
    refetchInterval: 300_000,
    retry: 1
  });
  const scannerQuery = useQuery({
    queryKey: ["scanner-summary"],
    queryFn: fetchScannerSummary,
    refetchInterval: stream.isConnected ? false : 5_000,
    retry: 2
  });

  const currentPortfolio = stream.isConnected && stream.portfolio ? stream.portfolio : portfolioQuery.data ?? null;
  const currentScanner = stream.isConnected && stream.scannerPairs.length > 0
    ? stream.scannerPairs
    : scannerQuery.data?.all_pairs ?? [];
  const currentPrice = stream.isConnected
    ? stream.livePrices[selectedSymbol] ?? marketQuery.data?.current_price ?? null
    : marketQuery.data?.current_price ?? null;

  const queryErrors = [portfolioQuery, marketQuery, signalQuery, newsQuery, scannerQuery]
    .filter((query) => query.isError)
    .map((query) => messageFor(query.error));

  const refreshDashboard = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ["portfolio"] }),
      queryClient.invalidateQueries({ queryKey: ["market-summary"] }),
      queryClient.invalidateQueries({ queryKey: ["ai-signal"] }),
      queryClient.invalidateQueries({ queryKey: ["news-sentiment"] }),
      queryClient.invalidateQueries({ queryKey: ["scanner-summary"] })
    ]);
  };

  const runAction = async (operation: () => Promise<{ message: string }>) => {
    try {
      const response = await operation();
      setActionNotice({ tone: "success", message: response.message });
      await refreshDashboard();
    } catch (error) {
      setActionNotice({ tone: "error", message: messageFor(error) });
    }
  };

  const handleToggleBotAction = (enable: boolean) =>
    runAction(() => toggleBot(enable));

  const handleSelectStrategyAction = (strategy: string) =>
    runAction(() => setStrategy(strategy, currentPortfolio?.risk_mode ?? "Moderate"));

  const handleSubmitOrderAction = (
    side: "LONG" | "SHORT",
    allocationUsd: number,
    leverage: number,
    orderType: string
  ) =>
    runAction(() => submitOrder({
      symbol: selectedSymbol,
      side,
      order_type: orderType,
      allocation_usd: allocationUsd,
      leverage
    }));

  const handlePositionActionClick = (symbol: string, action: "CLOSE" | "PARTIAL_CLOSE" | "REVERSE") =>
    runAction(() => handlePositionAction({ symbol, action, ratio: action === "PARTIAL_CLOSE" ? 0.5 : undefined }));

  const isLoading = portfolioQuery.isLoading && !currentPortfolio;

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500/30">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        collapsed={sidebarCollapsed}
        setCollapsed={setSidebarCollapsed}
        connectionState={stream.connectionState}
      />

      <div className={`flex-1 min-w-0 p-4 transition-all duration-300 lg:p-6 ${sidebarCollapsed ? "ml-20" : "ml-64"}`}>
        <Header
          portfolio={currentPortfolio}
          newsSentiment={newsQuery.data ?? null}
          latency={stream.latency}
          connectionState={stream.connectionState}
          onToggleBot={handleToggleBotAction}
          onSelectStrategy={handleSelectStrategyAction}
        />

        {(queryErrors.length > 0 || actionNotice || isLoading) && (
          <div className={`mb-6 flex items-start gap-3 rounded-2xl border px-4 py-3 text-sm ${
            actionNotice?.tone === "success"
              ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-200"
              : queryErrors.length > 0 || actionNotice?.tone === "error"
                ? "border-amber-500/30 bg-amber-500/10 text-amber-100"
                : "border-cyan-500/30 bg-cyan-500/10 text-cyan-100"
          }`}>
            {actionNotice?.tone === "success" ? <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0" /> : <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />}
            <div className="min-w-0 flex-1">
              {actionNotice ? actionNotice.message : isLoading ? "Loading portfolio data from the backend…" : queryErrors[0]}
            </div>
            {(queryErrors.length > 0 || actionNotice?.tone === "error") && (
              <button onClick={() => void refreshDashboard()} className="inline-flex items-center gap-1 text-xs font-semibold hover:text-white">
                <RefreshCw className="h-3.5 w-3.5" /> Retry
              </button>
            )}
          </div>
        )}

        <main className="space-y-6">
          <div className="grid grid-cols-1 gap-6 xl:grid-cols-4">
            <div className="min-w-0 xl:col-span-3">
              <TradingViewChart
                symbol={selectedSymbol}
                timeframe={timeframe}
                chartData={marketQuery.data?.chart_data ?? []}
                positions={currentPortfolio?.active_positions ?? []}
                currentPrice={currentPrice}
                onTimeframeChange={setTimeframe}
              />
            </div>

            <div className="min-w-0 space-y-6">
              <RightOrderPanel
                symbol={selectedSymbol}
                marketSummary={marketQuery.data ?? null}
                newsSentiment={newsQuery.data ?? null}
              />
              <ManualOrderForm
                symbol={selectedSymbol}
                currentPrice={currentPrice}
                onSubmitOrder={handleSubmitOrderAction}
              />
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <MarketScannerTable scannerPairs={currentScanner} onSelectSymbol={setSelectedSymbol} />
            <NewsSentimentPanel newsSentiment={newsQuery.data ?? null} aiSignal={signalQuery.data ?? null} />
          </div>

          <BottomTabsPanel portfolio={currentPortfolio} onPositionAction={handlePositionActionClick} />
        </main>

        <Footer
          dbSyncStatus={currentPortfolio?.database_sync_status}
          lastValidationTime={currentPortfolio?.last_validation_time}
          connectionState={stream.connectionState}
        />
      </div>
    </div>
  );
}
