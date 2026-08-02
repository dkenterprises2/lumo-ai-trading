"use client";

import { useMemo } from "react";
import { Candle } from "@/types/trading";

export interface IndicatorPoint {
  time: string | number;
  sma20?: number;
  sma50?: number;
  ema9?: number;
  ema21?: number;
  vwap?: number;
  bbUpper?: number;
  bbMiddle?: number;
  bbLower?: number;
  rsi?: number;
  macd?: number;
  macdSignal?: number;
  macdHist?: number;
  atr?: number;
}

export function useTechnicalIndicators(candles: Candle[]) {
  return useMemo(() => {
    if (!candles || candles.length === 0) return { indicatorPoints: [], processedCandles: [] };

    // Convert timestamps to unix timestamp (seconds) or YYYY-MM-DD
    const processedCandles = candles.map((c, index) => {
      let t: number;
      if (typeof c.timestamp === "number") {
        t = c.timestamp > 1e11 ? Math.floor(c.timestamp / 1000) : c.timestamp;
      } else {
        const parsed = new Date(c.timestamp).getTime();
        t = isNaN(parsed) ? index : Math.floor(parsed / 1000);
      }
      return { ...c, timeNum: t };
    }).sort((a, b) => a.timeNum - b.timeNum);

    const closes = processedCandles.map(c => c.close);

    // SMA Helper
    const calcSMA = (period: number): (number | undefined)[] => {
      return closes.map((val, idx) => {
        if (idx < period - 1) return undefined;
        const sum = closes.slice(idx - period + 1, idx + 1).reduce((a, b) => a + b, 0);
        return sum / period;
      });
    };

    // EMA Helper
    const calcEMA = (period: number): (number | undefined)[] => {
      const k = 2 / (period + 1);
      const res: (number | undefined)[] = [];
      let prevEma: number | undefined = undefined;

      closes.forEach((val, idx) => {
        if (idx < period - 1) {
          res.push(undefined);
        } else if (idx === period - 1) {
          const sum = closes.slice(0, period).reduce((a, b) => a + b, 0);
          prevEma = sum / period;
          res.push(prevEma);
        } else if (prevEma !== undefined) {
          prevEma = val * k + prevEma * (1 - k);
          res.push(prevEma);
        }
      });
      return res;
    };

    // VWAP Helper
    let cumVol = 0;
    let cumPV = 0;
    const vwapList = processedCandles.map(c => {
      const typicalPrice = (c.high + c.low + c.close) / 3;
      cumPV += typicalPrice * (c.volume || 1);
      cumVol += (c.volume || 1);
      return cumVol > 0 ? cumPV / cumVol : typicalPrice;
    });

    const sma20List = calcSMA(20);
    const sma50List = calcSMA(50);
    const ema9List = calcEMA(9);
    const ema21List = calcEMA(21);

    // Bollinger Bands Helper (20, 2)
    const bbUpper: (number | undefined)[] = [];
    const bbMiddle: (number | undefined)[] = [];
    const bbLower: (number | undefined)[] = [];

    closes.forEach((val, idx) => {
      if (idx < 19) {
        bbUpper.push(undefined);
        bbMiddle.push(undefined);
        bbLower.push(undefined);
      } else {
        const slice = closes.slice(idx - 19, idx + 1);
        const mean = slice.reduce((a, b) => a + b, 0) / 20;
        const variance = slice.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / 20;
        const stdDev = Math.sqrt(variance);
        bbMiddle.push(mean);
        bbUpper.push(mean + stdDev * 2);
        bbLower.push(mean - stdDev * 2);
      }
    });

    // RSI (14)
    const rsiList: (number | undefined)[] = [];
    let gains = 0;
    let losses = 0;

    for (let i = 0; i < closes.length; i++) {
      if (i === 0) {
        rsiList.push(undefined);
        continue;
      }
      const diff = closes[i] - closes[i - 1];
      if (i <= 14) {
        if (diff >= 0) gains += diff;
        else losses -= diff;

        if (i === 14) {
          const avgGain = gains / 14;
          const avgLoss = losses / 14;
          const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
          rsiList.push(100 - (100 / (1 + rs)));
        } else {
          rsiList.push(undefined);
        }
      } else {
        const prevAvgGain = gains / 14;
        const prevAvgLoss = losses / 14;
        const currGain = diff > 0 ? diff : 0;
        const currLoss = diff < 0 ? -diff : 0;

        gains = (prevAvgGain * 13 + currGain);
        losses = (prevAvgLoss * 13 + currLoss);

        const avgGain = gains / 14;
        const avgLoss = losses / 14;
        const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
        rsiList.push(100 - (100 / (1 + rs)));
      }
    }

    // MACD (12, 26, 9)
    const ema12 = calcEMA(12);
    const ema26 = calcEMA(26);
    const macdLine: (number | undefined)[] = [];

    closes.forEach((_, idx) => {
      const e12 = ema12[idx];
      const e26 = ema26[idx];
      if (e12 !== undefined && e26 !== undefined) {
        macdLine.push(e12 - e26);
      } else {
        macdLine.push(undefined);
      }
    });

    // MACD Signal (9-period EMA of MACD Line)
    const validMacdValues = macdLine.filter((v): v is number => v !== undefined);
    const macdSignalList: (number | undefined)[] = [];
    const k9 = 2 / 10;
    let prevSignal: number | undefined = undefined;

    let validCounter = 0;
    macdLine.forEach((val) => {
      if (val === undefined) {
        macdSignalList.push(undefined);
      } else {
        if (validCounter < 8) {
          macdSignalList.push(undefined);
        } else if (validCounter === 8) {
          const sum = validMacdValues.slice(0, 9).reduce((a, b) => a + b, 0);
          prevSignal = sum / 9;
          macdSignalList.push(prevSignal);
        } else if (prevSignal !== undefined) {
          prevSignal = val * k9 + prevSignal * (1 - k9);
          macdSignalList.push(prevSignal);
        }
        validCounter++;
      }
    });

    const indicatorPoints: IndicatorPoint[] = processedCandles.map((c, idx) => ({
      time: c.timeNum,
      sma20: sma20List[idx],
      sma50: sma50List[idx],
      ema9: ema9List[idx],
      ema21: ema21List[idx],
      vwap: vwapList[idx],
      bbUpper: bbUpper[idx],
      bbMiddle: bbMiddle[idx],
      bbLower: bbLower[idx],
      rsi: rsiList[idx],
      macd: macdLine[idx],
      macdSignal: macdSignalList[idx],
      macdHist: (macdLine[idx] !== undefined && macdSignalList[idx] !== undefined)
        ? (macdLine[idx]! - macdSignalList[idx]!)
        : undefined
    }));

    return { indicatorPoints, processedCandles };
  }, [candles]);
}
