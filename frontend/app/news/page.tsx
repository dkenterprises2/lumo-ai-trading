import React from 'react';
import { NewsIntelligenceDashboard } from '@/components/news/NewsIntelligenceDashboard';

export const metadata = {
  title: 'AI News Intelligence | Lumo AI Trading',
  description: 'Event classification, LLM reasoning, sentiment forecasting & risk signals'
};

export default function NewsPage() {
  return <NewsIntelligenceDashboard />;
}
