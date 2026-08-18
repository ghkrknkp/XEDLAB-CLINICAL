import React from "react";
import { ShieldCheck, AlertTriangle } from "lucide-react";

export default function ConfidenceBadge({ confidence }) {
  const percent = Math.round((confidence || 0.8) * 100);
  const isLow = percent < 65;

  return (
    <div className="inline-flex flex-col items-start gap-1">
      <span
        className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold ${
          isLow
            ? "bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800"
            : "bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800"
        }`}
        title={`Extraction confidence based on OCR certainty and document parsing structure: ${percent}%`}
      >
        {isLow ? <AlertTriangle className="w-3 h-3 text-amber-600" /> : <ShieldCheck className="w-3 h-3 text-emerald-600" />}
        Extraction: {percent}%
      </span>

      {isLow && (
        <span className="text-[10px] text-amber-600 dark:text-amber-400 font-medium">
          Verify against original report
        </span>
      )}
    </div>
  );
}
