"use client";

import React, { useEffect, useRef, useState } from "react";
import {
  createChart,
  IChartApi,
  CandlestickSeries,
  HistogramSeries,
  LineSeries,
  LineStyle,
  CrosshairMode,
  createSeriesMarkers,
  SeriesMarker,
  UTCTimestamp
} from "lightweight-charts";
import { Candle, Position } from "@/types/trading";
import { useTechnicalIndicators } from "@/hooks/useTechnicalIndicators";
import {
  Camera,
  Maximize2,
  Minimize2,
  RotateCcw,
  Activity,
} from "lucide-react";

interface TradingViewChartProps {
  symbol: string;
  timeframe: string;
  chartData: Candle[];
  positions: Position[];
  currentPrice: number | null;
  onTimeframeChange: (tf: string) => void;
}

export function TradingViewChart({
  symbol,
  timeframe,
  chartData,
  positions,
  currentPrice,
  onTimeframeChange
}: TradingViewChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ReturnType<IChartApi["addSeries"]> | null>(null);
  const priceLineRef = useRef<ReturnType<ReturnType<IChartApi["addSeries"]>["createPriceLine"]> | null>(null);

  // Indicator Toggle State
  const [showSMA20, setShowSMA20] = useState(true);
  const [showSMA50, setShowSMA50] = useState(false);
  const [showEMA9, setShowEMA9] = useState(true);
  const [showEMA21, setShowEMA21] = useState(false);
  const [showVWAP, setShowVWAP] = useState(true);
  const [showBB, setShowBB] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Indicators calculations
  const { indicatorPoints, processedCandles } = useTechnicalIndicators(chartData);
  const candlesList = processedCandles;

  // Active Position for current symbol
  const activePosition = positions.find(p => p.symbol === symbol);

  useEffect(() => {
    if (!containerRef.current || candlesList.length === 0) return;

    // Create TradingView Lightweight Chart
    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: 440,
      layout: {
        background: { color: "#090d16" },
        textColor: "#94a3b8"
      },
      grid: {
        vertLines: { color: "rgba(30, 41, 59, 0.5)" },
        horzLines: { color: "rgba(30, 41, 59, 0.5)" }
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: {
          color: "#00f2fe",
          width: 1,
          style: LineStyle.Dashed
        },
        horzLine: {
          color: "#00f2fe",
          width: 1,
          style: LineStyle.Dashed
        }
      },
      rightPriceScale: {
        borderColor: "#1e293b"
      },
      timeScale: {
        borderColor: "#1e293b",
        timeVisible: true,
        secondsVisible: false
      }
    });

    chartRef.current = chart;
    candleSeriesRef.current = null;
    priceLineRef.current = null;

    // 1. Candlestick Series
    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#00e676",
      downColor: "#ff1744",
      borderUpColor: "#00e676",
      borderDownColor: "#ff1744",
      wickUpColor: "#00e676",
      wickDownColor: "#ff1744"
    });

    candleSeriesRef.current = candleSeries;

    const formattedCandles = candlesList.map(c => ({
      time: c.timeNum as UTCTimestamp,
      open: c.open,
      high: c.high,
      low: c.low,
      close: c.close
    }));

    candleSeries.setData(formattedCandles);

    // 2. Volume Histogram Series
    const volumeSeries = chart.addSeries(HistogramSeries, {
      color: "#00f2fe",
      priceFormat: { type: "volume" },
      priceScaleId: "volume"
    });

    chart.priceScale("volume").applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 }
    });


    volumeSeries.setData(
      candlesList.map(c => ({
        time: c.timeNum as UTCTimestamp,
        value: c.volume || 1,
        color: c.close >= c.open ? "rgba(0, 230, 118, 0.3)" : "rgba(255, 23, 68, 0.3)"
      }))
    );

    // 3. Technical Indicators Line Overlays
    if (showSMA20) {
      const sma20Series = chart.addSeries(LineSeries, { color: "#ffd600", lineWidth: 2, priceLineVisible: false });
      sma20Series.setData(
        indicatorPoints
          .filter(p => p.sma20 !== undefined)
          .map(p => ({ time: p.time as UTCTimestamp, value: p.sma20! }))
      );
    }

    if (showSMA50) {
      const sma50Series = chart.addSeries(LineSeries, { color: "#ff9100", lineWidth: 2, priceLineVisible: false });
      sma50Series.setData(
        indicatorPoints
          .filter(p => p.sma50 !== undefined)
          .map(p => ({ time: p.time as UTCTimestamp, value: p.sma50! }))
      );
    }

    if (showEMA9) {
      const ema9Series = chart.addSeries(LineSeries, { color: "#a855f7", lineWidth: 2, priceLineVisible: false });
      ema9Series.setData(
        indicatorPoints
          .filter(p => p.ema9 !== undefined)
          .map(p => ({ time: p.time as UTCTimestamp, value: p.ema9! }))
      );
    }

    if (showEMA21) {
      const ema21Series = chart.addSeries(LineSeries, { color: "#ec4899", lineWidth: 2, priceLineVisible: false });
      ema21Series.setData(
        indicatorPoints
          .filter(p => p.ema21 !== undefined)
          .map(p => ({ time: p.time as UTCTimestamp, value: p.ema21! }))
      );
    }

    if (showVWAP) {
      const vwapSeries = chart.addSeries(LineSeries, { color: "#00f2fe", lineWidth: 2, lineStyle: LineStyle.Dotted, priceLineVisible: false });
      vwapSeries.setData(
        indicatorPoints
          .filter(p => p.vwap !== undefined)
          .map(p => ({ time: p.time as UTCTimestamp, value: p.vwap! }))
      );
    }

    if (showBB) {
      const bbUpperSeries = chart.addSeries(LineSeries, { color: "rgba(148, 163, 184, 0.6)", lineWidth: 1, lineStyle: LineStyle.Dashed, priceLineVisible: false });
      const bbLowerSeries = chart.addSeries(LineSeries, { color: "rgba(148, 163, 184, 0.6)", lineWidth: 1, lineStyle: LineStyle.Dashed, priceLineVisible: false });
      
      bbUpperSeries.setData(
        indicatorPoints
          .filter(p => p.bbUpper !== undefined)
          .map(p => ({ time: p.time as UTCTimestamp, value: p.bbUpper! }))
      );
      bbLowerSeries.setData(
        indicatorPoints
          .filter(p => p.bbLower !== undefined)
          .map(p => ({ time: p.time as UTCTimestamp, value: p.bbLower! }))
      );
    }



    // 4. Trade Visualization Overlays & Price Lines
    if (activePosition) {
      const posSide = activePosition.side;

      // Entry Price Line
      candleSeries.createPriceLine({
        price: activePosition.entry_price,
        color: posSide === "LONG" ? "#00e676" : "#ff1744",
        lineWidth: 2,
        lineStyle: LineStyle.Solid,
        axisLabelVisible: true,
        title: `${posSide} Entry: $${activePosition.entry_price}`
      });

      // Take Profit Line
      if (activePosition.take_profit_price) {
        candleSeries.createPriceLine({
          price: activePosition.take_profit_price,
          color: "#00e676",
          lineWidth: 1,
          lineStyle: LineStyle.Dashed,
          axisLabelVisible: true,
          title: `Take Profit: $${activePosition.take_profit_price}`
        });
      }

      // Stop Loss Line
      if (activePosition.stop_loss_price) {
        candleSeries.createPriceLine({
          price: activePosition.stop_loss_price,
          color: "#ff1744",
          lineWidth: 1,
          lineStyle: LineStyle.Dashed,
          axisLabelVisible: true,
          title: `Stop Loss: $${activePosition.stop_loss_price}`
        });
      }

      // Liquidation Line
      if (activePosition.liquidation_price) {
        candleSeries.createPriceLine({
          price: activePosition.liquidation_price,
          color: "#a855f7",
          lineWidth: 1,
          lineStyle: LineStyle.LargeDashed,
          axisLabelVisible: true,
          title: `Liquidation: $${activePosition.liquidation_price}`
        });
      }

    }



    
    
    

    // Set markers for open trades
    const markers: SeriesMarker<UTCTimestamp>[] = [];
    if (activePosition && candlesList.length > 0) {
      const lastCandle = candlesList[candlesList.length - 1];
      markers.push({
        time: lastCandle.timeNum as UTCTimestamp,
        position: activePosition.side === "LONG" ? "belowBar" : "aboveBar",
        color: activePosition.side === "LONG" ? "#00e676" : "#ff1744",
        shape: activePosition.side === "LONG" ? "arrowUp" : "arrowDown",
        text: `${activePosition.side} ${activePosition.leverage}x`
      });
    }

    createSeriesMarkers(candleSeries, markers);



    // Fit Content
    chart.timeScale().fitContent();

    // Handle Resize
    const handleResize = () => {
      if (containerRef.current && chartRef.current) {
        chartRef.current.applyOptions({ width: containerRef.current.clientWidth });
      }
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      candleSeriesRef.current = null;
      chart.remove();
    };
  }, [candlesList, indicatorPoints, showSMA20, showSMA50, showEMA9, showEMA21, showVWAP, showBB, activePosition]);

  // Update price line separately when currentPrice changes
  useEffect(() => {
    if (!candleSeriesRef.current) return;
    const candleSeries = candleSeriesRef.current;
    
    // Remove existing price line
    if (priceLineRef.current) {
      candleSeries.removePriceLine(priceLineRef.current);
      priceLineRef.current = null;
    }
    
    // Add new price line
    if (currentPrice !== null && currentPrice > 0) {
      priceLineRef.current = candleSeries.createPriceLine({
        price: currentPrice,
        color: "#00f2fe",
        lineWidth: 1,
        lineStyle: LineStyle.Dotted,
        axisLabelVisible: true,
        title: "Current price"
      });
    }
  }, [currentPrice]);

  // Actions
  const handleResetZoom = () => {
    if (chartRef.current) chartRef.current.timeScale().fitContent();
  };

  const handleTakeScreenshot = () => {
    if (chartRef.current) {
      const canvas = chartRef.current.takeScreenshot();
      const link = document.createElement("a");
      link.download = `Lumo_TradingView_${symbol.replace("/", "_")}_${timeframe}.png`;
      link.href = canvas.toDataURL();
      link.click();
    }
  };

  const handleToggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  return (
    <div className={`p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl space-y-4 ${
      isFullscreen ? "fixed inset-0 z-50 rounded-none bg-slate-950 p-6 overflow-auto" : ""
    }`}>
      {/* Header Toolbar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-cyan-500/10 text-cyan-400">
            <Activity className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-bold text-slate-100 text-base flex items-center gap-2">
              TradingView Professional Terminal
              <span className="text-xs px-2 py-0.5 rounded-md bg-cyan-500/10 text-cyan-400 font-mono">
                {symbol} • {timeframe}
              </span>
            </h3>
          </div>
        </div>

        {/* Timeframe & Indicator Toggles */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Timeframe Buttons */}
          <div className="flex items-center gap-1 p-1 rounded-xl bg-slate-950 border border-slate-800 text-xs">
            {["1m", "5m", "15m", "1H", "4H", "1D"].map((tf) => (
              <button
                key={tf}
                onClick={() => onTimeframeChange(tf)}
                className={`px-2.5 py-1 rounded-lg font-medium transition ${
                  timeframe === tf
                    ? "bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md shadow-cyan-500/20"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {tf}
              </button>
            ))}
          </div>

          {/* Indicator Quick Toggles */}
          <div className="flex items-center gap-1.5 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800 text-xs font-mono">
            <button
              onClick={() => setShowSMA20(!showSMA20)}
              className={`px-2 py-0.5 rounded ${showSMA20 ? "bg-amber-500/20 text-amber-400" : "text-slate-500"}`}
            >
              SMA20
            </button>
            <button
              onClick={() => setShowSMA50(!showSMA50)}
              className={`px-2 py-0.5 rounded ${showSMA50 ? "bg-orange-500/20 text-orange-400" : "text-slate-500"}`}
            >
              SMA50
            </button>
            <button
              onClick={() => setShowEMA9(!showEMA9)}
              className={`px-2 py-0.5 rounded ${showEMA9 ? "bg-purple-500/20 text-purple-400" : "text-slate-500"}`}
            >
              EMA9
            </button>
            <button
              onClick={() => setShowEMA21(!showEMA21)}
              className={`px-2 py-0.5 rounded ${showEMA21 ? "bg-pink-500/20 text-pink-400" : "text-slate-500"}`}
            >
              EMA21
            </button>
            <button
              onClick={() => setShowVWAP(!showVWAP)}
              className={`px-2 py-0.5 rounded ${showVWAP ? "bg-cyan-500/20 text-cyan-400" : "text-slate-500"}`}
            >
              VWAP
            </button>
            <button
              onClick={() => setShowBB(!showBB)}
              className={`px-2 py-0.5 rounded ${showBB ? "bg-slate-700 text-slate-200" : "text-slate-500"}`}
            >
              BB
            </button>
          </div>

          {/* Tools: Reset, Screenshot, Fullscreen */}
          <div className="flex items-center gap-1">
            <button
              onClick={handleResetZoom}
              title="Reset Zoom / Fit Content"
              className="p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-400 hover:text-slate-100 hover:border-slate-700 transition"
            >
              <RotateCcw className="h-4 w-4" />
            </button>
            <button
              onClick={handleTakeScreenshot}
              title="Take Chart Screenshot"
              className="p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-400 hover:text-slate-100 hover:border-slate-700 transition"
            >
              <Camera className="h-4 w-4" />
            </button>
            <button
              onClick={handleToggleFullscreen}
              title="Toggle Fullscreen"
              className="p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-400 hover:text-slate-100 hover:border-slate-700 transition"
            >
              {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
            </button>
          </div>
        </div>
      </div>

      {/* Chart Canvas Container */}
      <div ref={containerRef} className="w-full h-[440px] rounded-xl overflow-hidden relative border border-slate-800/60">
        {/* Active Trade Banner Overlay */}
        {activePosition && (
          <div className="absolute top-3 left-3 z-10 p-2.5 rounded-xl bg-slate-950/80 backdrop-blur-md border border-slate-800 font-mono text-xs space-y-1">
            <div className="flex items-center gap-2">
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                activePosition.side === "LONG" ? "bg-emerald-500/20 text-emerald-400" : "bg-rose-500/20 text-rose-400"
              }`}>
                {activePosition.side} {activePosition.leverage}x
              </span>
              <span className="text-slate-300 font-bold">{activePosition.symbol}</span>
            </div>
            <div className="text-slate-400">
              Entry: <span className="text-slate-100 font-bold">${activePosition.entry_price}</span> | PnL: <span className={`font-bold ${activePosition.unrealized_pnl_usd >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                {activePosition.unrealized_pnl_usd >= 0 ? "+" : ""}${activePosition.unrealized_pnl_usd.toFixed(2)}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
