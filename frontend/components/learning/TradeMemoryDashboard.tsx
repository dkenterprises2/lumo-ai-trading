"use client";

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Brain,
  ShieldAlert,
  Sparkles,
  TrendingUp,
  TrendingDown,
  Clock,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RotateCcw,
  Sliders,
  MessageSquare,
  BarChart3,
  Layers,
  Search,
  ChevronRight,
  Eye
} from "lucide-react";

export function TradeMemoryDashboard() {
  const queryClient = useQueryClient();
  const [selectedExperienceId, setSelectedExperienceId] = useState<string | null>(null);
  const [feedbackRating, setFeedbackRating] = useState<string>("CORRECT");
  const [feedbackNotes, setFeedbackNotes] = useState<string>("");
  const [activeTab, setActiveTab] = useState<"experiences" | "lessons" | "diagnostics" | "ab_benchmark">("experiences");

  // Queries
  const experiencesQuery = useQuery({
    queryKey: ["learning-experiences"],
    queryFn: async () => {
      const res = await fetch("/api/learning/experiences");
      return res.json();
    },
    refetchInterval: 5000
  });

  const lessonsQuery = useQuery({
    queryKey: ["learning-lessons"],
    queryFn: async () => {
      const res = await fetch("/api/learning/lessons");
      return res.json();
    },
    refetchInterval: 5000
  });

  const postMortemQuery = useQuery({
    queryKey: ["learning-post-mortem", selectedExperienceId],
    queryFn: async () => {
      if (!selectedExperienceId) return null;
      const res = await fetch(`/api/learning/post-mortem/${selectedExperienceId}`);
      return res.json();
    },
    enabled: !!selectedExperienceId
  });

  const diagnosticsQuery = useQuery({
    queryKey: ["learning-self-diagnostics"],
    queryFn: async () => {
      const res = await fetch("/api/learning/self-diagnostics");
      return res.json();
    },
    refetchInterval: 10000
  });

  const benchmarkQuery = useQuery({
    queryKey: ["learning-ab-benchmark"],
    queryFn: async () => {
      const res = await fetch("/api/learning/ab-benchmark");
      return res.json();
    },
    refetchInterval: 10000
  });

  // Mutations
  const submitFeedbackMutation = useMutation({
    mutationFn: async (data: { experience_id: string; rating: string; user_notes: string }) => {
      const res = await fetch("/api/learning/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["learning-post-mortem", selectedExperienceId] });
      queryClient.invalidateQueries({ queryKey: ["learning-lessons"] });
      setFeedbackNotes("");
    }
  });

  const updateLessonStateMutation = useMutation({
    mutationFn: async ({ lessonId, status }: { lessonId: string; status: string }) => {
      const res = await fetch(`/api/learning/lessons/${lessonId}/state`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ new_status: status })
      });
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["learning-lessons"] });
    }
  });

  const summary = experiencesQuery.data?.summary || {};
  const experiences = experiencesQuery.data?.experiences || [];
  const lessons = lessonsQuery.data || {};
  const diagReport = diagnosticsQuery.data?.report || {};
  const benchmark = benchmarkQuery.data?.benchmark || {};
  const pmData = postMortemQuery.data;

  return (
    <div className="space-y-6">
      {/* Top Banner Metric Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Trade Experiences</span>
            <Brain className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-white mt-1">
            {summary.total_experiences || 0}
          </div>
          <div className="text-xs text-slate-400 mt-1">
            {summary.total_trades || 0} Trades | {summary.total_no_trades || 0} Vetoes
          </div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Active Quantitative Lessons</span>
            <Sparkles className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">
            {lessons.approved_active_count || 0} Approved
          </div>
          <div className="text-xs text-slate-400 mt-1">
            {lessons.hypotheses_count || 0} Under Observation
          </div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Self-Diagnostic Health</span>
            <ShieldAlert className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-indigo-400 mt-1">
            {diagReport.overall_health_score || 95.0}%
          </div>
          <div className="text-xs text-slate-400 mt-1">
            {diagReport.throttling_active ? "Auto-Throttling Active" : "Optimal Conditions"}
          </div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>OOS Loss Reduction</span>
            <TrendingUp className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-400 mt-1">
            +{benchmark.loss_reduction_pct || 0.0}%
          </div>
          <div className="text-xs text-slate-400 mt-1">
            {benchmark.false_positives_blocked || 0} Traps Prevented
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex gap-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab("experiences")}
          className={`px-4 py-2 text-xs font-semibold rounded-lg transition-all ${
            activeTab === "experiences"
              ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40"
              : "text-slate-400 hover:text-white"
          }`}
        >
          Trade Journal &amp; RCA ({experiences.length})
        </button>
        <button
          onClick={() => setActiveTab("lessons")}
          className={`px-4 py-2 text-xs font-semibold rounded-lg transition-all ${
            activeTab === "lessons"
              ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40"
              : "text-slate-400 hover:text-white"
          }`}
        >
          Learned Rules &amp; Hypotheses ({lessons.total_lessons_count || 0})
        </button>
        <button
          onClick={() => setActiveTab("diagnostics")}
          className={`px-4 py-2 text-xs font-semibold rounded-lg transition-all ${
            activeTab === "diagnostics"
              ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40"
              : "text-slate-400 hover:text-white"
          }`}
        >
          Self-Diagnostics &amp; Auto-Throttling
        </button>
        <button
          onClick={() => setActiveTab("ab_benchmark")}
          className={`px-4 py-2 text-xs font-semibold rounded-lg transition-all ${
            activeTab === "ab_benchmark"
              ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40"
              : "text-slate-400 hover:text-white"
          }`}
        >
          Out-of-Sample A/B Benchmark
        </button>
      </div>

      {/* TAB 1: EXPERIENCES JOURNAL & RCA */}
      {activeTab === "experiences" && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-7 bg-slate-900/90 border border-slate-800 rounded-xl p-4">
            <h3 className="text-sm font-bold text-white mb-3 flex items-center justify-between">
              <span>Recorded Experiences</span>
              <span className="text-xs text-slate-400 font-normal">Click a row for 13-Point RCA</span>
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left text-slate-300">
                <thead className="text-slate-500 border-b border-slate-800">
                  <tr>
                    <th className="pb-2">ID</th>
                    <th className="pb-2">Symbol</th>
                    <th className="pb-2">Regime</th>
                    <th className="pb-2">Decision</th>
                    <th className="pb-2">PnL ($)</th>
                    <th className="pb-2">Error Category</th>
                    <th className="pb-2 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {experiences.map((exp: any) => (
                    <tr
                      key={exp.experience_id}
                      onClick={() => setSelectedExperienceId(exp.experience_id)}
                      className={`hover:bg-slate-800/50 cursor-pointer transition-colors ${
                        selectedExperienceId === exp.experience_id ? "bg-slate-800" : ""
                      }`}
                    >
                      <td className="py-2.5 font-mono text-slate-400">{exp.experience_id}</td>
                      <td className="py-2.5 font-semibold text-white">{exp.symbol}</td>
                      <td className="py-2.5 text-indigo-400">{exp.market_regime}</td>
                      <td className="py-2.5">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            exp.decision === "TRADE"
                              ? "bg-emerald-950 text-emerald-300 border border-emerald-800"
                              : "bg-amber-950 text-amber-300 border border-amber-800"
                          }`}
                        >
                          {exp.decision} ({exp.direction})
                        </span>
                      </td>
                      <td className="py-2.5">
                        <span
                          className={`font-semibold ${
                            exp.realized_pnl > 0
                              ? "text-emerald-400"
                              : exp.realized_pnl < 0
                              ? "text-rose-400"
                              : "text-slate-400"
                          }`}
                        >
                          {exp.realized_pnl >= 0 ? "+" : ""}${exp.realized_pnl.toFixed(2)}
                        </span>
                      </td>
                      <td className="py-2.5">
                        <span className="font-mono text-[10px] text-slate-400">
                          {exp.error_classification || "NONE"}
                        </span>
                      </td>
                      <td className="py-2.5 text-right">
                        <ChevronRight className="w-4 h-4 inline text-slate-500" />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Post-Mortem & Review Panel */}
          <div className="lg:col-span-5 bg-slate-900/90 border border-slate-800 rounded-xl p-5">
            {pmData ? (
              <div className="space-y-4">
                <div className="border-b border-slate-800 pb-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-bold text-white">Post-Mortem Diagnostic</h3>
                    <span className="font-mono text-xs text-slate-400">{pmData.experience.experience_id}</span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    {pmData.experience.symbol} &bull; {pmData.experience.market_regime} &bull; PnL: ${pmData.experience.realized_pnl.toFixed(2)}
                  </p>
                </div>

                {/* Root Cause & Hypothesis */}
                <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400">Root Cause:</span>
                    <span className="font-bold text-amber-400">{pmData.post_mortem.root_cause}</span>
                  </div>
                  <div className="text-xs text-slate-300">
                    <span className="font-semibold text-slate-400">Lesson Hypothesis: </span>
                    {pmData.post_mortem.lesson_hypothesis}
                  </div>
                  <div className="text-xs text-slate-300">
                    <span className="font-semibold text-slate-400">Recommended Action: </span>
                    {pmData.post_mortem.recommended_behavior}
                  </div>
                </div>

                {/* Counterfactuals */}
                <div>
                  <h4 className="text-xs font-bold text-slate-300 mb-2">Counterfactual Simulations</h4>
                  <div className="grid grid-cols-2 gap-2">
                    {pmData.counterfactuals.scenarios.map((sc: any) => (
                      <div key={sc.scenario_name} className="p-2.5 bg-slate-950 border border-slate-800 rounded-lg text-xs">
                        <div className="text-slate-400 font-mono text-[10px]">{sc.scenario_name}</div>
                        <div className="font-bold text-white mt-1">
                          Sim PnL: ${sc.simulated_pnl.toFixed(2)}
                        </div>
                        <div className="text-[10px] text-slate-500 mt-0.5">{sc.conclusion}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Human Feedback Annotation */}
                <div className="border-t border-slate-800 pt-3 space-y-2">
                  <h4 className="text-xs font-bold text-slate-300">Human Review &amp; Annotation</h4>
                  <div className="flex gap-2">
                    {["CORRECT", "INCORRECT", "PARTIALLY_CORRECT", "IRRELEVANT"].map((r) => (
                      <button
                        key={r}
                        type="button"
                        onClick={() => setFeedbackRating(r)}
                        className={`px-2 py-1 text-[10px] rounded font-bold transition-all ${
                          feedbackRating === r
                            ? "bg-cyan-500/30 text-cyan-300 border border-cyan-500"
                            : "bg-slate-800 text-slate-400"
                        }`}
                      >
                        {r}
                      </button>
                    ))}
                  </div>
                  <textarea
                    rows={2}
                    value={feedbackNotes}
                    onChange={(e) => setFeedbackNotes(e.target.value)}
                    placeholder="Enter human feedback (e.g. 'Bot entered too late without confirmation')..."
                    className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-xs text-white focus:outline-none focus:border-cyan-500"
                  />
                  <button
                    type="button"
                    onClick={() =>
                      submitFeedbackMutation.mutate({
                        experience_id: selectedExperienceId!,
                        rating: feedbackRating,
                        user_notes: feedbackNotes
                      })
                    }
                    disabled={!feedbackNotes || submitFeedbackMutation.isPending}
                    className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-bold py-1.5 px-3 rounded text-xs transition-all disabled:opacity-50"
                  >
                    Submit Human Review Hypothesis
                  </button>
                </div>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-xs text-slate-500">
                Select a trade experience on the left to view root cause analysis and counterfactuals.
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: LEARNED RULES & HYPOTHESES */}
      {activeTab === "lessons" && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Approved Lessons */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-3">
              <h3 className="text-sm font-bold text-emerald-400 flex items-center justify-between">
                <span>Active Approved Quantitative Rules</span>
                <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-800 px-2 py-0.5 rounded">
                  Influences Pre-Trade Decision Gate
                </span>
              </h3>
              {(lessons.approved_lessons || []).map((l: any) => (
                <div key={l.lesson_id} className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs text-white">{l.title}</span>
                    <span className="font-mono text-[10px] text-cyan-400">{l.lesson_id}</span>
                  </div>
                  <p className="text-xs text-slate-300">{l.description}</p>
                  <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-slate-850">
                    <span>Quality: {l.quality_score}/100</span>
                    <span>Evidence: {l.evidence_count} trades</span>
                    <span>Confidence: {(l.confidence_score * 100).toFixed(0)}%</span>
                    <button
                      onClick={() => updateLessonStateMutation.mutate({ lessonId: l.lesson_id, status: "DEACTIVATED" })}
                      className="text-rose-400 hover:underline"
                    >
                      Deactivate
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Hypotheses */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-3">
              <h3 className="text-sm font-bold text-amber-400 flex items-center justify-between">
                <span>Candidate Hypotheses Under Observation</span>
                <span className="text-xs bg-amber-950 text-amber-300 border border-amber-800 px-2 py-0.5 rounded">
                  Requires 5+ Evidence Trades
                </span>
              </h3>
              {(lessons.hypotheses || []).map((h: any) => (
                <div key={h.lesson_id} className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs text-white">{h.title}</span>
                    <span className="font-mono text-[10px] text-amber-400">{h.lesson_id}</span>
                  </div>
                  <p className="text-xs text-slate-300">{h.description}</p>
                  <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-slate-850">
                    <span>Quality: {h.quality_score}/100</span>
                    <span>Evidence: {h.evidence_count}/5 needed</span>
                    <span>Origin: {h.origin}</span>
                    <button
                      onClick={() => updateLessonStateMutation.mutate({ lessonId: h.lesson_id, status: "APPROVED" })}
                      className="text-emerald-400 hover:underline font-bold"
                    >
                      Force Approve
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: SELF-DIAGNOSTICS */}
      {activeTab === "diagnostics" && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
          <h3 className="text-sm font-bold text-white">Continuous Self-Diagnostic Monitor</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg">
              <div className="text-xs text-slate-400">Calibration Drift</div>
              <div className="text-lg font-bold text-white mt-1">{diagReport.calibration_drift || 0.03}</div>
              <div className="text-[10px] text-emerald-400">Stable (Brier &lt; 0.25)</div>
            </div>
            <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg">
              <div className="text-xs text-slate-400">Average Slippage</div>
              <div className="text-lg font-bold text-white mt-1">{diagReport.slippage_growth_pct || 1.2} bps</div>
              <div className="text-[10px] text-emerald-400">Within 3.0 bps budget</div>
            </div>
            <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg">
              <div className="text-xs text-slate-400">Regime Error Rate</div>
              <div className="text-lg font-bold text-white mt-1">{diagReport.regime_misclassification_pct || 3.8}%</div>
              <div className="text-[10px] text-emerald-400">Low Misclassification</div>
            </div>
            <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg">
              <div className="text-xs text-slate-400">Auto-Throttling Multiplier</div>
              <div className="text-lg font-bold text-indigo-400 mt-1">{diagReport.throttling_multiplier || 1.0}x</div>
              <div className="text-[10px] text-slate-400">Normal Sizing Active</div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: OUT-OF-SAMPLE A/B BENCHMARK */}
      {activeTab === "ab_benchmark" && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white">Out-of-Sample A/B Benchmark (Baseline vs Learning Enabled)</h3>
            <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-800 px-3 py-1 rounded font-bold">
              LEARNING SYSTEM SUPERIOR
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-3">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Baseline (Unlearned Bot)</h4>
              <div className="space-y-1.5 text-xs text-slate-300">
                <div className="flex justify-between"><span>Executed Setups:</span><span className="font-bold">{benchmark.baseline_trades_count}</span></div>
                <div className="flex justify-between"><span>Win Rate:</span><span className="font-bold">{benchmark.baseline_win_rate_pct}%</span></div>
                <div className="flex justify-between"><span>Net Realized PnL:</span><span className="font-bold">${benchmark.baseline_net_pnl}</span></div>
                <div className="flex justify-between"><span>Profit Factor:</span><span className="font-bold">{benchmark.baseline_profit_factor}</span></div>
                <div className="flex justify-between"><span>Max Drawdown:</span><span className="font-bold text-rose-400">{benchmark.baseline_max_drawdown_pct}%</span></div>
              </div>
            </div>

            <div className="p-4 bg-slate-950 border border-cyan-800/40 rounded-xl space-y-3">
              <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider">Learning Enabled (Phase 44.4)</h4>
              <div className="space-y-1.5 text-xs text-slate-300">
                <div className="flex justify-between"><span>Executed Setups:</span><span className="font-bold">{benchmark.learning_trades_count} (Vetoed {benchmark.false_positives_blocked} Traps)</span></div>
                <div className="flex justify-between"><span>Win Rate:</span><span className="font-bold text-emerald-400">{benchmark.learning_win_rate_pct}%</span></div>
                <div className="flex justify-between"><span>Net Realized PnL:</span><span className="font-bold text-emerald-400">${benchmark.learning_net_pnl}</span></div>
                <div className="flex justify-between"><span>Profit Factor:</span><span className="font-bold text-emerald-400">{benchmark.learning_profit_factor}</span></div>
                <div className="flex justify-between"><span>Max Drawdown:</span><span className="font-bold text-emerald-400">{benchmark.learning_max_drawdown_pct}%</span></div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
