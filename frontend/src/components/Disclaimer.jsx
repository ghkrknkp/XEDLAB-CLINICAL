import React from "react";
import { ShieldAlert } from "lucide-react";

export default function Disclaimer() {
  return (
    <div className="flex items-start gap-3 rounded-xl border border-amber-500/30 bg-amber-500/5 dark:bg-amber-500/10 px-4 py-3.5 text-xs text-slate-700 dark:text-slate-300">
      <ShieldAlert className="w-4 h-4 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
      <div>
        <span className="font-semibold text-amber-700 dark:text-amber-400">
          Medical Safety Notice:{" "}
        </span>
        AI Medical Report Analyzer is an informational document-analysis tool. It does not provide medical diagnosis or treatment advice. Laboratory reference ranges may vary by laboratory, method, age, sex, and other factors. Always consult a qualified healthcare professional for interpretation of medical results.
      </div>
    </div>
  );
}
