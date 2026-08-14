import React from 'react';
import { ArbitrageDashboard } from '@/components/arbitrage/ArbitrageDashboard';

export const metadata = {
  title: 'Cross-Exchange Arbitrage | Lumo AI Trading',
  description: 'Multi-exchange arbitrage intelligence, spot-perp basis & funding rate heatmap'
};

export default function ArbitragePage() {
  return <ArbitrageDashboard />;
}
