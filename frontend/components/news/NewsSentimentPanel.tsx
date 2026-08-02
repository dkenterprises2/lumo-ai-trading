"use client";

import React from "react";
import { NewsSentiment, AiSignal } from "@/types/trading";
import { Flame, Newspaper, ExternalLink, Bot } from "lucide-react";

interface NewsSentimentPanelProps {
  newsSentiment: NewsSentiment | null;
  aiSignal: AiSignal | null;
}

export function NewsSentimentPanel({ newsSentiment, aiSignal }: NewsSentimentPanelProps) {
  const fearVal = newsSentiment?.fear_greed.value ?? 50;
  const fearLabel = newsSentiment?.fear_greed.classification ?? "Neutral";
  const newsAvg = newsSentiment?.sentiment_summary.news_score_avg ?? 50;
  const newsLabel = newsSentiment?.sentiment_summary.label ?? "Neutral";

  const isBuySignal = aiSignal?.action.includes("BUY");
  const isSellSignal = aiSignal?.action.includes("SELL");

  return (
    <div className="space-y-4">
      {/* AI Signal Card */}
      {aiSignal && (
        <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800/80">
            <div className="flex items-center gap-2">
              <Bot className="h-5 w-5 text-cyan-400" />
              <h3 className="font-bold text-slate-100 text-sm">AI Quantitative Signal</h3>
            </div>
            <span
              className={`px-2.5 py-0.5 rounded-lg text-xs font-bold ${
                isBuySignal
                  ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                  : isSellSignal
                  ? "bg-rose-500/10 text-rose-400 border border-rose-500/30"
                  : "bg-slate-800 text-slate-300"
              }`}
            >
              {aiSignal.action.replace("_", " ")}
            </span>
          </div>

          <div className="flex items-center justify-between text-xs font-mono">
            <div className="flex items-center gap-1.5">
              <span className="text-slate-400">Direction:</span>
              <span className="font-bold text-slate-200">{aiSignal.direction}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-slate-400">Confidence:</span>
              <span className="font-bold text-cyan-400">{aiSignal.confidence_score}%</span>
            </div>
          </div>

          <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-emerald-400 flex items-center justify-between">
            <span>SL: ${aiSignal.stop_loss_price} (-{aiSignal.stop_loss_pct}%)</span>
            <span>TP: ${aiSignal.take_profit_price} (+{aiSignal.take_profit_pct}%)</span>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/50 p-2.5 rounded-xl border border-slate-800/50">
            {aiSignal.reasoning}
          </p>
        </div>
      )}

      {/* News & Sentiment Feed */}
      <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-purple-500/10 text-purple-400">
              <Newspaper className="h-5 w-5" />
            </div>
            <div>
              <h3 className="font-bold text-slate-100 text-base">Market Sentiment & News</h3>
              <p className="text-xs text-slate-400">Fear & Greed Index + Live Articles</p>
            </div>
          </div>
        </div>

        {/* Fear & Greed Meter */}
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <div className="flex items-center justify-between text-slate-400">
              <span>Fear & Greed</span>
              <Flame className="h-4 w-4 text-amber-400" />
            </div>
            <div className="text-lg font-bold text-slate-100 font-mono">
              {fearVal} <span className="text-xs font-normal text-slate-400">({fearLabel})</span>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <div className="flex items-center justify-between text-slate-400">
              <span>News Sentiment</span>
              <Newspaper className="h-4 w-4 text-purple-400" />
            </div>
            <div className="text-lg font-bold text-purple-400 font-mono">
              {newsAvg} <span className="text-xs font-normal text-slate-400">({newsLabel})</span>
            </div>
          </div>
        </div>

        {/* News List */}
        <div className="space-y-2 max-h-60 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-800">
          {newsSentiment?.news_articles.map((art, idx) => (
            <div
              key={idx}
              className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-slate-700 transition space-y-1"
            >
              <div className="flex items-center justify-between">
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    art.sentiment === "Bullish"
                      ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                      : "bg-rose-500/10 text-rose-400 border border-rose-500/30"
                  }`}
                >
                  {art.sentiment}
                </span>
                <span className="text-[10px] text-slate-500">{art.source}</span>
              </div>
              <a
                href={art.link}
                target="_blank"
                rel="noreferrer"
                className="text-xs font-medium text-slate-200 hover:text-cyan-400 transition line-clamp-2 flex items-center justify-between gap-1 group"
              >
                <span>{art.title}</span>
                <ExternalLink className="h-3 w-3 text-slate-500 group-hover:text-cyan-400 shrink-0" />
              </a>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
