import React, { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import FileUploader from "../components/FileUploader";
import ProcessingStatus from "../components/ProcessingStatus";
import Disclaimer from "../components/Disclaimer";
import { reports as reportsApi } from "../services/api";
import { getAllReports } from "../services/localStore";
import { FileText, Clock, CheckCircle2, ArrowRight, Activity, Sparkles, ShieldCheck, Stethoscope } from "lucide-react";

export default function Dashboard() {
  const navigate = useNavigate();
  const [activeJob, setActiveJob] = useState(null);
  const [recentReports, setRecentReports] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchRecent = async () => {
    try {
      const res = await reportsApi.list();
      setRecentReports(res.data || []);
    } catch (err) {
      const localData = getAllReports();
      setRecentReports(localData || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecent();
  }, []);

  const handleUploadSuccess = (uploadData) => {
    if (uploadData.job_id === "local") {
      fetchRecent();
      navigate(`/reports/${uploadData.report_id}`);
    } else {
      setActiveJob(uploadData);
    }
  };

  const handleJobComplete = () => {
    if (activeJob) {
      const repId = activeJob.report_id;
      setActiveJob(null);
      fetchRecent();
      navigate(`/reports/${repId}`);
    }
  };

  return (
    <div className="flex min-h-screen text-slate-100 font-sans">
      <Sidebar />

      <main className="flex-1 p-6 sm:p-10 max-w-6xl mx-auto">
        {/* Banner Header */}
        <div className="mb-8 p-6 sm:p-8 rounded-3xl glass-panel relative overflow-hidden">
          <div className="absolute -right-10 -bottom-10 opacity-10 pointer-events-none">
            <Stethoscope className="w-64 h-64 text-teal-400" />
          </div>

          <div className="relative z-10 flex flex-wrap items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-teal-500/20 border border-teal-400/40 text-teal-300 text-xs font-semibold shadow-inner">
                  <Sparkles className="w-3.5 h-3.5 text-teal-400" /> AI Document Intelligence
                </span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight drop-shadow-sm">
                Medical Report Intelligence
              </h1>
              <p className="text-xs sm:text-sm text-slate-300 mt-1.5 font-normal max-w-2xl leading-relaxed">
                Upload laboratory documents for deterministic reference range checking, explainable confidence scoring, grounded summaries, and isolated RAG Q&A.
              </p>
            </div>

            <Link
              to="/history"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold bg-teal-500/20 hover:bg-teal-500/30 border border-teal-400/40 text-teal-200 hover:text-white shadow-lg transition-all"
            >
              <Clock className="w-4 h-4 text-teal-400" /> View History
            </Link>
          </div>
        </div>

        {/* Active Processing Box */}
        {activeJob && (
          <div className="mb-8 animate-in fade-in duration-300">
            <ProcessingStatus
              reportId={activeJob.report_id}
              onComplete={handleJobComplete}
              localMode={activeJob.job_id === "local"}
            />
          </div>
        )}

        {/* Main Uploader */}
        <div className="mb-10">
          <FileUploader onUploadSuccess={handleUploadSuccess} />
        </div>

        {/* Recent Reports Section */}
        <div className="glass-panel rounded-3xl p-6 sm:p-8 shadow-2xl mb-8">
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-teal-500/20 border border-teal-400/30 text-teal-300 flex items-center justify-center shadow-md">
                <Activity className="w-4 h-4" />
              </div>
              <h2 className="text-sm sm:text-base font-extrabold text-white uppercase tracking-wider">
                Recent Analyzed Reports
              </h2>
            </div>
            <span className="text-xs text-slate-300 font-medium">Showing latest {Math.min(recentReports.length, 5)}</span>
          </div>

          {loading ? (
            <div className="py-8 text-center text-xs text-slate-300 font-medium">Loading recent reports...</div>
          ) : recentReports.length === 0 ? (
            <div className="py-10 text-center border border-dashed border-slate-700/80 rounded-2xl bg-slate-950/40 p-6">
              <FileText className="w-8 h-8 mx-auto mb-2 text-slate-500" />
              <p className="text-xs font-bold text-slate-200">No medical reports uploaded yet.</p>
              <p className="text-[11px] text-slate-400 mt-1 font-normal">Use the dropzone above or click a 1-click sample to begin.</p>
            </div>
          ) : (
            <div className="divide-y divide-slate-800/80">
              {recentReports.slice(0, 5).map((r) => (
                <div
                  key={r.report_id}
                  onClick={() => navigate(`/reports/${r.report_id}`)}
                  className="py-4 px-3 flex items-center justify-between gap-4 hover:bg-slate-800/40 rounded-2xl cursor-pointer transition-all group"
                >
                  <div className="flex items-center gap-3.5">
                    <div className="w-10 h-10 rounded-xl bg-teal-500/20 border border-teal-400/30 text-teal-300 flex items-center justify-center flex-shrink-0 shadow-md">
                      <FileText className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="text-xs sm:text-sm font-bold text-white group-hover:text-teal-300 transition-colors">
                        {r.filename}
                      </h4>
                      <div className="flex items-center gap-2 text-[11px] text-slate-300 mt-1 font-medium">
                        <span className="font-mono text-teal-300 font-semibold">{r.report_id}</span>
                        <span>•</span>
                        <span className="font-bold text-white">{r.report_type}</span>
                        <span>•</span>
                        <span>{r.created_at ? new Date(r.created_at).toLocaleDateString() : 'Today'}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span
                      className={`text-[11px] font-bold px-3 py-1 rounded-full capitalize ${
                        r.processing_status === "completed" || r.processing_status === "analyzed"
                          ? "bg-teal-500/20 text-teal-200 border border-teal-400/40"
                          : r.processing_status === "failed"
                          ? "bg-rose-500/20 text-rose-200 border border-rose-400/40"
                          : "bg-amber-500/20 text-amber-200 border border-amber-400/40 animate-pulse"
                      }`}
                    >
                      {r.processing_status}
                    </span>
                    <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-teal-300 group-hover:translate-x-0.5 transition-all" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Disclaimer */}
        <Disclaimer />
      </main>
    </div>
  );
}
