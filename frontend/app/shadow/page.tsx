'use client';

import React, { useState } from 'react';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { ShadowTradingDashboard } from '@/components/shadow/ShadowTradingDashboard';
import { useTradingStream } from '@/hooks/useTradingStream';
import { useQuery } from '@tanstack/react-query';
import { fetchPortfolio, fetchNewsSentiment, toggleBot, setStrategy } from '@/services/api';

export default function ShadowPage() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const stream = useTradingStream();

  const portfolioQuery = useQuery({ queryKey: ["portfolio"], queryFn: fetchPortfolio, refetchInterval: 5000 });
  const newsQuery = useQuery({ queryKey: ["news-sentiment"], queryFn: fetchNewsSentiment, refetchInterval: 300000 });

  const currentPortfolio = stream.isConnected && stream.portfolio ? stream.portfolio : portfolioQuery.data ?? null;

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 selection:bg-purple-500/30">
      <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} connectionState={stream.connectionState} />
      <div className={`flex-1 min-w-0 p-4 transition-all duration-300 lg:p-6 ${sidebarCollapsed ? "ml-20" : "ml-64"}`}>
        <Header 
          portfolio={currentPortfolio} 
          newsSentiment={newsQuery.data ?? null} 
          latency={stream.latency} 
          connectionState={stream.connectionState} 
          onToggleBot={(enable) => toggleBot(enable)} 
          onSelectStrategy={(s) => setStrategy(s)} 
        />
        <main className="space-y-6">
          <ShadowTradingDashboard />
        </main>
        <Footer dbSyncStatus="SYNCED" connectionState={stream.connectionState} />
      </div>
    </div>
  );
}
