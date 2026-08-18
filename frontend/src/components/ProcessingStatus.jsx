import React, { useEffect, useState } from "react";
import {
  FileText,
  Scan,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Clock,
  Layers,
  Search,
  Cpu,
  BarChart2,
} from "lucide-react";
import { reports as reportsApi } from "../services/api";
import { getStatus } from "../services/localStore";

const STAGES = [
  { id: "QUEUED", label: "Queued", icon: Clock, desc: "Waiting for worker" },
  { id: "EXTRACTING", label: "Extracting", icon: FileText, desc: "Reading PDF/Doc" },
  { id: "OCR_PROCESSING", label: "OCR Scan", icon: Scan, desc: "Scanning document" },
  { id: "CLEANING", label: "Cleaning", icon: Layers, desc: "Normalizing text" },
  { id: "CLASSIFYING", label: "Classifying", icon: Sparkles, desc: "Detecting report type" },
  { id: "ENTITY_EXTRACTION", label: "Entities", icon: Search, desc: "Extracting metadata" },
  { id: "LAB_EXTRACTION", label: "Lab Results", icon: BarChart2, desc: "Parsing measurements" },
  { id: "VALIDATION", label: "Validating", icon: Cpu, desc: "Checking ranges" },
  { id: "SUMMARY", label: "Summary", icon: Sparkles, desc: "Grounded explanation" },
  { id: "INDEXING", label: "Indexing", icon: Layers, desc: "Vector chunking" },
  { id: "COMPLETED", label: "Completed", icon: CheckCircle2, desc: "Ready to view" },
];

export default function ProcessingStatus({ reportId, onComplete, localMode }) {
  const [jobStatus, setJobStatus] = useState({
    status: "processing",
    stage: "EXTRACTING",
    progress: 15,
    message: null,
  });
  const [error, setError] = useState(null);

  useEffect(() => {
    let intervalId;
    let isMounted = true;

    if (localMode) {
      let stageIndex = 0;
      intervalId = setInterval(() => {
        if (!isMounted) return;
        stageIndex++;
        if (stageIndex >= STAGES.length - 1) {
          clearInterval(intervalId);
          setJobStatus({ status: "completed", stage: "COMPLETED", progress: 100 });
          if (onComplete) setTimeout(onComplete, 600);
        } else {
          setJobStatus({
            status: "processing",
            stage: STAGES[stageIndex].id,
            progress: Math.floor((stageIndex / (STAGES.length - 1)) * 100)
          });
        }
      }, 300);
      return () => {
        isMounted = false;
        clearInterval(intervalId);
      };
    }

    const pollStatus = async () => {
      try {
        const res = await reportsApi.status(reportId);
        if (!isMounted) return;

        setJobStatus(res.data);

        if (res.data.status === "completed" || res.data.stage === "COMPLETED") {
          clearInterval(intervalId);
          if (onComplete) {
            setTimeout(onComplete, 600);
          }
        } else if (res.data.status === "failed" || res.data.stage === "FAILED") {
          clearInterval(intervalId);
          setError(res.data.message || "Document processing could not be completed.");
        }
      } catch (err) {
        const localData = getStatus(reportId);
        if (localData && (localData.status === "completed" || localData.stage === "COMPLETED")) {
          if (!isMounted) return;
          setJobStatus(localData);
          clearInterval(intervalId);
          if (onComplete) {
            setTimeout(onComplete, 600);
          }
        }
      }
    };

    pollStatus();
    intervalId = setInterval(pollStatus, 1500);

    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, [reportId, onComplete, localMode]);

  const currentStageIndex = STAGES.findIndex((s) => s.id === jobStatus.stage);
  const activeIndex = currentStageIndex >= 0 ? currentStageIndex : 1;

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/50 px-2.5 py-1 rounded-full">
            Background Analysis in Progress
          </span>
          <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-100 mt-2">
            Analyzing Report #{reportId}
          </h3>
        </div>
        <div className="text-right">
          <span className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
            {jobStatus.progress || 10}%
          </span>
          <p className="text-xs text-slate-500">Stage: {jobStatus.stage || "PROCESSING"}</p>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-slate-100 dark:bg-slate-800 h-2.5 rounded-full overflow-hidden mb-6">
        <div
          className="bg-gradient-to-r from-emerald-500 to-teal-400 h-full transition-all duration-500 rounded-full"
          style={{ width: `${Math.max(jobStatus.progress || 5, 8)}%` }}
        />
      </div>

      {error ? (
        <div className="flex items-start gap-3 p-4 bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-800 rounded-xl text-rose-700 dark:text-rose-300">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-sm">Processing Failed</h4>
            <p className="text-xs mt-0.5">{error}</p>
          </div>
        </div>
      ) : (
        /* Stepper */
        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-11 gap-2 pt-2">
          {STAGES.map((stage, idx) => {
            const Icon = stage.icon;
            const isDone = idx < activeIndex || jobStatus.status === "completed";
            const isCurrent = idx === activeIndex && jobStatus.status !== "completed";

            return (
              <div
                key={stage.id}
                className={`flex flex-col items-center text-center p-2 rounded-xl border transition-all ${
                  isCurrent
                    ? "border-emerald-500 bg-emerald-50/50 dark:bg-emerald-950/30 shadow-xs ring-1 ring-emerald-400/20"
                    : isDone
                    ? "border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 text-slate-700 dark:text-slate-300"
                    : "border-transparent opacity-40 text-slate-400"
                }`}
              >
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center mb-1.5 ${
                    isCurrent
                      ? "bg-emerald-600 text-white animate-pulse"
                      : isDone
                      ? "bg-emerald-100 dark:bg-emerald-900 text-emerald-700 dark:text-emerald-300"
                      : "bg-slate-100 dark:bg-slate-800 text-slate-400"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                </div>
                <span className="text-[11px] font-medium truncate w-full">{stage.label}</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
