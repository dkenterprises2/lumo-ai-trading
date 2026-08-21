'use client';

import React, { useEffect, useRef } from 'react';
import {
  createChart,
  IChartApi,
  CandlestickSeries,
  HistogramSeries,
  CrosshairMode,
  LineStyle,
  UTCTimestamp
} from 'lightweight-charts';

export interface ShadowReplayCandle {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface ShadowReplayChartProps {
  candles: ShadowReplayCandle[];
  currentIndex: number;
  symbol: string;
  timeframe: string;
  isReplayActive?: boolean;
}

export const ShadowReplayChart: React.FC<ShadowReplayChartProps> = ({
  candles,
  currentIndex,
  symbol,
  timeframe,
  isReplayActive = false
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<any>(null);
  const volumeSeriesRef = useRef<any>(null);
  const lastIndexRef = useRef<number>(-1);
  const lastDatasetRef = useRef<ShadowReplayCandle[]>([]);

  useEffect(() => {
    if (!containerRef.current) return;

    const initialWidth = containerRef.current.clientWidth || 800;
    const chart = createChart(containerRef.current, {
      width: initialWidth,
      height: 440,
      layout: {
        background: { color: '#090d16' },
        textColor: '#94a3b8'
      },
      grid: {
        vertLines: { color: 'rgba(30, 41, 59, 0.4)' },
        horzLines: { color: 'rgba(30, 41, 59, 0.4)' }
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: {
          color: '#00f2fe',
          width: 1,
          style: LineStyle.Dashed
        },
        horzLine: {
          color: '#00f2fe',
          width: 1,
          style: LineStyle.Dashed
        }
      },
      rightPriceScale: {
        borderColor: '#1e293b',
        scaleMargins: {
          top: 0.1,
          bottom: 0.25
        }
      },
      timeScale: {
        borderColor: '#1e293b',
        timeVisible: true,
        secondsVisible: false
      }
    });

    chartRef.current = chart;

    // 1. Candlestick Series
    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#10b981',
      downColor: '#f43f5e',
      borderVisible: false,
      wickUpColor: '#10b981',
      wickDownColor: '#f43f5e'
    });
    candleSeriesRef.current = candleSeries;

    // 2. Volume Series
    const volumeSeries = chart.addSeries(HistogramSeries, {
      color: '#6366f1',
      priceFormat: {
        type: 'volume'
      },
      priceScaleId: '', // Overlay pane
    });
    volumeSeries.priceScale().applyOptions({
      scaleMargins: {
        top: 0.8,
        bottom: 0
      }
    });
    volumeSeriesRef.current = volumeSeries;

    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        if (entry.contentRect.width > 0 && chartRef.current) {
          chartRef.current.applyOptions({
            width: Math.floor(entry.contentRect.width)
          });
        }
      }
    });

    resizeObserver.observe(containerRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
      chartRef.current = null;
      candleSeriesRef.current = null;
      volumeSeriesRef.current = null;
      lastIndexRef.current = -1;
      lastDatasetRef.current = [];
    };
  }, []);

  // Formatting helpers
  const formatCandle = (c: ShadowReplayCandle) => ({
    time: Math.floor(c.time) as UTCTimestamp,
    open: c.open,
    high: c.high,
    low: c.low,
    close: c.close
  });

  const formatVolume = (c: ShadowReplayCandle) => ({
    time: Math.floor(c.time) as UTCTimestamp,
    value: c.volume,
    color: c.close >= c.open ? 'rgba(16, 185, 129, 0.4)' : 'rgba(244, 63, 94, 0.4)'
  });

  // High-Performance Stream & Render with O(1) updates
  useEffect(() => {
    if (!candleSeriesRef.current || !volumeSeriesRef.current || !candles || candles.length === 0) return;

    const isNewDataset = lastDatasetRef.current !== candles;
    const isRestart = currentIndex <= lastIndexRef.current || isNewDataset || !isReplayActive;

    if (isRestart) {
      // Rebuild initial dataset
      const visibleCount = isReplayActive ? Math.max(1, currentIndex + 1) : candles.length;
      const initialSlice = candles.slice(0, visibleCount);

      candleSeriesRef.current.setData(initialSlice.map(formatCandle));
      volumeSeriesRef.current.setData(initialSlice.map(formatVolume));

      lastIndexRef.current = visibleCount - 1;
      lastDatasetRef.current = candles;

      if (chartRef.current) {
        if (isReplayActive) {
          chartRef.current.timeScale().scrollToRealTime();
        } else {
          chartRef.current.timeScale().fitContent();
        }
      }
    } else {
      // Incremental O(1) Fast Stream Updates for 60-120fps smooth animation
      const startIdx = Math.max(0, lastIndexRef.current + 1);
      for (let i = startIdx; i <= currentIndex && i < candles.length; i++) {
        const c = candles[i];
        candleSeriesRef.current.update(formatCandle(c));
        volumeSeriesRef.current.update(formatVolume(c));
      }
      lastIndexRef.current = currentIndex;
      if (chartRef.current && isReplayActive) {
        chartRef.current.timeScale().scrollToRealTime();
      }
    }
  }, [candles, currentIndex, isReplayActive]);

  const currentCandle = candles[currentIndex] || candles[candles.length - 1];

  return (
    <div className="bg-slate-950/80 border border-slate-800 rounded-2xl p-4 shadow-xl space-y-3">
      {/* Candle Header HUD */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800/80 pb-2.5">
        <div className="flex items-center space-x-3">
          <span className="text-sm font-bold font-mono text-cyan-400">{symbol}</span>
          <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-xs font-mono font-bold uppercase">
            {timeframe}
          </span>
          {isReplayActive ? (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-extrabold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              REPLAY STREAMING (60 FPS)
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
              ● READY ({candles.length} CANDLES)
            </span>
          )}
        </div>

        {currentCandle && (
          <div className="flex flex-wrap items-center gap-3 text-xs font-mono">
            <span className="text-slate-400">
              O: <strong className="text-slate-200">${currentCandle.open.toLocaleString()}</strong>
            </span>
            <span className="text-slate-400">
              H: <strong className="text-emerald-400">${currentCandle.high.toLocaleString()}</strong>
            </span>
            <span className="text-slate-400">
              L: <strong className="text-rose-400">${currentCandle.low.toLocaleString()}</strong>
            </span>
            <span className="text-slate-400">
              C: <strong className={currentCandle.close >= currentCandle.open ? 'text-emerald-400' : 'text-rose-400'}>
                ${currentCandle.close.toLocaleString()}
              </strong>
            </span>
            <span className="text-slate-400">
              Vol: <strong className="text-indigo-300">{currentCandle.volume.toLocaleString()}</strong>
            </span>
            <span className="text-slate-500">
              {new Date(currentCandle.time * 1000).toLocaleDateString()}
            </span>
          </div>
        )}
      </div>

      {/* Chart Canvas Container */}
      <div ref={containerRef} className="w-full relative min-h-[420px]" />
    </div>
  );
};
