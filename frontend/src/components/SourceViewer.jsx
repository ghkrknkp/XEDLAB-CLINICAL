import React, { useState } from "react";
import { FileText, Scan, Search, ChevronLeft, ChevronRight } from "lucide-react";

export default function SourceViewer({ pages = [], highlightedSnippet = "" }) {
  const [currentPageIndex, setCurrentPageIndex] = useState(0);
  const [searchFilter, setSearchFilter] = useState("");

  if (!pages || pages.length === 0) {
    return (
      <div className="p-8 text-center bg-slate-50 dark:bg-slate-900 rounded-2xl border border-dashed border-slate-200 dark:border-slate-800 text-slate-500">
        <FileText className="w-8 h-8 mx-auto mb-2 opacity-40" />
        <p className="text-sm font-medium">No source page text available for this report.</p>
      </div>
    );
  }

  const currentPage = pages[currentPageIndex] || pages[0];
  const textLines = (currentPage.text || "").split("\n");

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs overflow-hidden">
      {/* Header Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-4 bg-slate-50/80 dark:bg-slate-800/40 border-b border-slate-200 dark:border-slate-800">
        <div className="flex items-center gap-3">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Document Source Attribution
          </span>
          <span
            className={`inline-flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-full ${
              currentPage.ocr_used
                ? "bg-purple-50 dark:bg-purple-950 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800"
                : "bg-blue-50 dark:bg-blue-950 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800"
            }`}
          >
            {currentPage.ocr_used ? <Scan className="w-3 h-3" /> : <FileText className="w-3 h-3" />}
            {currentPage.ocr_used ? "Tesseract OCR Extraction" : "Selectable PDF Text"}
          </span>
        </div>

        {/* Page Switcher */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setCurrentPageIndex((prev) => Math.max(0, prev - 1))}
            disabled={currentPageIndex === 0}
            className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="text-xs font-medium text-slate-700 dark:text-slate-300 px-1">
            Page {currentPage.page} of {pages.length}
          </span>
          <button
            onClick={() => setCurrentPageIndex((prev) => Math.min(pages.length - 1, prev + 1))}
            disabled={currentPageIndex === pages.length - 1}
            className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Page Content */}
      <div className="p-5 font-mono text-xs text-slate-800 dark:text-slate-200 bg-slate-50/30 dark:bg-slate-950/30 max-h-96 overflow-y-auto whitespace-pre-wrap leading-relaxed divide-y divide-slate-100 dark:divide-slate-800/40">
        {textLines.map((line, idx) => {
          const isHighlighted =
            highlightedSnippet &&
            line.toLowerCase().includes(highlightedSnippet.toLowerCase().trim());

          return (
            <div
              key={idx}
              className={`py-1 px-2 rounded-sm transition-colors ${
                isHighlighted
                  ? "bg-amber-100/80 dark:bg-amber-950/60 font-semibold text-amber-900 dark:text-amber-200 border-l-2 border-amber-500 pl-2"
                  : "hover:bg-slate-100/50 dark:hover:bg-slate-800/30"
              }`}
            >
              <span className="text-slate-400 select-none inline-block w-8 text-right mr-3 text-[10px]">
                {idx + 1}
              </span>
              {line || " "}
            </div>
          );
        })}
      </div>
    </div>
  );
}
