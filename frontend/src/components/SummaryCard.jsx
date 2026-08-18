import React from "react";
import { Sparkles, ShieldAlert, CheckCircle2, AlertTriangle, HelpCircle, FileText } from "lucide-react";
import Disclaimer from "./Disclaimer";

export default function SummaryCard({ summaryData }) {
  if (!summaryData) return null;

  const {
    report_type = "Medical",
    total_findings = 0,
    within_range = 0,
    below_range = 0,
    above_range = 0,
    unknown = 0,
    summary = "",
    summary_source = "deterministic_fallback",
  } = summaryData;

  const outsideRange = below_range + above_range;

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-xs">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-emerald-50 dark:bg-emerald-950 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">
              Patient-Friendly Report Summary
            </h2>
            <p className="text-xs text-slate-500">
              Grounded synthesis of extracted report findings
            </p>
          </div>
        </div>

        {/* Source Provider Badge */}
        <span
          className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider ${
            summary_source.includes("openai") || summary_source.includes("gemini")
              ? "bg-blue-50 dark:bg-blue-950 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800"
              : "bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800"
          }`}
        >
          <Sparkles className="w-3 h-3" />
          Provider: {summary_source}
        </span>
      </div>

      {/* Metrics Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
        <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-2 text-slate-500 text-xs font-medium mb-1">
            <FileText className="w-3.5 h-3.5" /> Total Findings
          </div>
          <span className="text-xl font-bold text-slate-900 dark:text-white">{total_findings}</span>
        </div>

        <div className="p-3.5 rounded-xl bg-emerald-50/60 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800">
          <div className="flex items-center gap-2 text-emerald-700 dark:text-emerald-400 text-xs font-medium mb-1">
            <CheckCircle2 className="w-3.5 h-3.5" /> Within Range
          </div>
          <span className="text-xl font-bold text-emerald-700 dark:text-emerald-400">{within_range}</span>
        </div>

        <div className="p-3.5 rounded-xl bg-rose-50/60 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-800">
          <div className="flex items-center gap-2 text-rose-700 dark:text-rose-400 text-xs font-medium mb-1">
            <AlertTriangle className="w-3.5 h-3.5" /> Outside Range
          </div>
          <span className="text-xl font-bold text-rose-700 dark:text-rose-400">{outsideRange}</span>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-2 text-slate-500 text-xs font-medium mb-1">
            <HelpCircle className="w-3.5 h-3.5" /> Unclassified
          </div>
          <span className="text-xl font-bold text-slate-600 dark:text-slate-300">{unknown}</span>
        </div>
      </div>

      {/* Summary Narrative */}
      <div className="prose dark:prose-invert max-w-none text-sm text-slate-700 dark:text-slate-300 bg-slate-50/50 dark:bg-slate-950/40 p-4 rounded-xl border border-slate-200 dark:border-slate-800 leading-relaxed whitespace-pre-line mb-4">
        {summary || "No summary text generated."}
      </div>

      {/* Disclaimer */}
      <Disclaimer />
    </div>
  );
}
