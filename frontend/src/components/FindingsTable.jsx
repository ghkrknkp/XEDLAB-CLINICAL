import React, { useState } from "react";
import { Filter, ArrowDown, ArrowUp, Check, HelpCircle, FileText } from "lucide-react";
import ConfidenceBadge from "./ConfidenceBadge";

export default function FindingsTable({ findings = [], onSelectSource }) {
  const [statusFilter, setStatusFilter] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");

  const filteredFindings = findings.filter((f) => {
    // Filter by search
    if (searchTerm && !f.test_name.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }
    // Filter by status
    if (statusFilter === "outside") {
      return f.status === "below_reference_range" || f.status === "above_reference_range";
    }
    if (statusFilter === "within") {
      return f.status === "within_reference_range";
    }
    if (statusFilter === "unclassified") {
      return f.status === "not_classified" || f.status === "unknown";
    }
    return true;
  });

  const getStatusBadge = (status) => {
    switch (status) {
      case "within_reference_range":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
            <Check className="w-3 h-3" /> Within Range
          </span>
        );
      case "below_reference_range":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 dark:bg-amber-950/50 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
            <ArrowDown className="w-3 h-3" /> Below Range
          </span>
        );
      case "above_reference_range":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 dark:bg-rose-950/50 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800">
            <ArrowUp className="w-3 h-3" /> Above Range
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700">
            <HelpCircle className="w-3 h-3" /> Not Classified
          </span>
        );
    }
  };

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs overflow-hidden">
      {/* Controls Header */}
      <div className="p-4 bg-slate-50/60 dark:bg-slate-800/40 border-b border-slate-200 dark:border-slate-800 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2 flex-1 min-w-[200px]">
          <input
            type="text"
            placeholder="Search test names (e.g. Hemoglobin, Glucose)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full max-w-sm px-3.5 py-1.5 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
          />
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setStatusFilter("all")}
            className={`px-3 py-1 text-xs font-medium rounded-lg transition-colors ${
              statusFilter === "all"
                ? "bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900"
                : "bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800"
            }`}
          >
            All ({findings.length})
          </button>
          <button
            onClick={() => setStatusFilter("outside")}
            className={`px-3 py-1 text-xs font-medium rounded-lg transition-colors ${
              statusFilter === "outside"
                ? "bg-rose-600 text-white"
                : "bg-white dark:bg-slate-900 text-rose-600 dark:text-rose-400 border border-rose-200 dark:border-rose-900/50 hover:bg-rose-50 dark:hover:bg-rose-950/30"
            }`}
          >
            Outside Range
          </button>
          <button
            onClick={() => setStatusFilter("within")}
            className={`px-3 py-1 text-xs font-medium rounded-lg transition-colors ${
              statusFilter === "within"
                ? "bg-emerald-600 text-white"
                : "bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-900/50 hover:bg-emerald-50 dark:hover:bg-emerald-950/30"
            }`}
          >
            Within Range
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50/40 dark:bg-slate-800/20 text-slate-500 font-semibold uppercase tracking-wider text-[11px]">
              <th className="py-3 px-4">Test Name</th>
              <th className="py-3 px-4">Observed Value</th>
              <th className="py-3 px-4">Unit</th>
              <th className="py-3 px-4">Printed Reference Range</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Confidence</th>
              <th className="py-3 px-4 text-right">Source</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 text-slate-700 dark:text-slate-300">
            {filteredFindings.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-8 text-center text-slate-400">
                  No findings match the selected filter.
                </td>
              </tr>
            ) : (
              filteredFindings.map((f, idx) => (
                <tr
                  key={idx}
                  className="hover:bg-slate-50/60 dark:hover:bg-slate-800/30 transition-colors"
                >
                  <td className="py-3 px-4 font-semibold text-slate-900 dark:text-white">
                    {f.test_name}
                  </td>
                  <td className="py-3 px-4 font-mono font-bold text-sm text-slate-900 dark:text-white">
                    {f.value !== null ? f.value : "—"}
                  </td>
                  <td className="py-3 px-4 text-slate-500 font-medium">
                    {f.unit || "—"}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-600 dark:text-slate-400">
                    {f.original_reference_text || f.reference_text || (f.reference_low !== null && f.reference_high !== null ? `${f.reference_low} - ${f.reference_high}` : "Not printed")}
                  </td>
                  <td className="py-3 px-4">
                    {getStatusBadge(f.status)}
                  </td>
                  <td className="py-3 px-4">
                    <ConfidenceBadge confidence={f.confidence} />
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => onSelectSource && onSelectSource(f.source)}
                      className="inline-flex items-center gap-1 text-xs text-emerald-600 dark:text-emerald-400 font-medium hover:underline px-2 py-1 rounded-md hover:bg-emerald-50 dark:hover:bg-emerald-950/50"
                      title="View source page excerpt in document viewer"
                    >
                      <FileText className="w-3.5 h-3.5" />
                      Page {f.source?.page || 1}
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
