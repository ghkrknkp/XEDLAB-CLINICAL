import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Disclaimer from "../components/Disclaimer";
import { reports as reportsApi } from "../services/api";
import { getAllReports, deleteReport as deleteLocalReport } from "../services/localStore";
import {
  FileText,
  Search,
  Filter,
  Trash2,
  ArrowRight,
  Sparkles,
  Calendar,
  Clock,
} from "lucide-react";

export default function History() {
  const navigate = useNavigate();
  const [reportsList, setReportsList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");

  const loadHistory = async () => {
    try {
      const res = await reportsApi.history();
      setReportsList(res.data || []);
    } catch (err) {
      const localData = getAllReports();
      setReportsList(localData || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleDelete = async (e, reportId) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to permanently delete this report?")) {
      return;
    }
    try {
      await reportsApi.remove(reportId).catch(() => {});
      deleteLocalReport(reportId);
      setReportsList((prev) => prev.filter((r) => r.report_id !== reportId));
    } catch (err) {
      alert("Failed to delete report.");
    }
  };

  const filteredReports = reportsList.filter((r) => {
    if (searchTerm) {
      const matchName = r.filename.toLowerCase().includes(searchTerm.toLowerCase());
      const matchId = r.report_id.toLowerCase().includes(searchTerm.toLowerCase());
      if (!matchName && !matchId) return false;
    }
    if (typeFilter !== "all" && r.report_type !== typeFilter) {
      return false;
    }
    return true;
  });

  const availableTypes = Array.from(new Set(reportsList.map((r) => r.report_type).filter(Boolean)));

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 font-sans">
      <Sidebar />

      <main className="flex-1 p-6 sm:p-10 max-w-6xl mx-auto">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Report History
            </h1>
            <p className="text-xs text-slate-400 mt-1 font-light max-w-2xl">
              Browse, search, and manage your previously analyzed medical reports and clinical findings.
            </p>
          </div>

          <button
            onClick={() => navigate("/dashboard")}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-teal-500 to-cyan-500 hover:from-teal-400 hover:to-cyan-400 text-slate-950 font-bold text-xs rounded-xl shadow-md shadow-teal-500/20 transition-all"
          >
            Upload New Report
          </button>
        </div>

        {/* Filters Card */}
        <div className="bg-slate-900/90 backdrop-blur-xl rounded-2xl border border-slate-800 p-4 shadow-xl mb-6 flex flex-wrap items-center justify-between gap-3">
          <div className="relative flex-1 min-w-[220px]">
            <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search reports by filename or ID (e.g. REP-10291)..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2.5 text-xs rounded-xl border border-slate-700 bg-slate-950 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-teal-500/30 focus:border-teal-500"
            />
          </div>

          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-500" />
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="text-xs rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5 text-slate-300 focus:outline-none focus:ring-2 focus:ring-teal-500/30"
            >
              <option value="all">All Report Types</option>
              {availableTypes.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Reports List */}
        <div className="bg-slate-900/90 backdrop-blur-xl rounded-3xl border border-slate-800 shadow-xl overflow-hidden mb-8">
          {loading ? (
            <div className="p-12 text-center text-xs text-slate-400">Loading report history...</div>
          ) : filteredReports.length === 0 ? (
            <div className="p-12 text-center">
              <FileText className="w-10 h-10 mx-auto text-slate-600 mb-2" />
              <h3 className="text-sm font-bold text-slate-300">
                No reports found
              </h3>
              <p className="text-xs text-slate-400 mt-1 font-light">
                {searchTerm || typeFilter !== "all"
                  ? "Try adjusting your search query or filter."
                  : "Upload your first medical report to view analysis history."}
              </p>
            </div>
          ) : (
            <div className="divide-y divide-slate-800/80">
              {filteredReports.map((r) => (
                <div
                  key={r.report_id}
                  onClick={() => navigate(`/reports/${r.report_id}`)}
                  className="p-5 flex flex-wrap items-center justify-between gap-4 hover:bg-slate-950/60 cursor-pointer transition-all group"
                >
                  <div className="flex items-center gap-3.5">
                    <div className="w-10 h-10 rounded-2xl bg-teal-950 border border-teal-500/30 text-teal-300 flex items-center justify-center flex-shrink-0">
                      <FileText className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-xs font-bold text-white group-hover:text-teal-300 transition-colors">
                        {r.filename}
                      </h3>
                      <div className="flex flex-wrap items-center gap-2 text-[11px] text-slate-400 mt-1">
                        <span className="font-mono text-slate-400 bg-slate-950 border border-slate-800 px-2 py-0.5 rounded">
                          {r.report_id}
                        </span>
                        <span>•</span>
                        <span className="font-semibold text-teal-300">
                          {r.report_type}
                        </span>
                        <span>•</span>
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" /> {r.created_at ? new Date(r.created_at).toLocaleDateString() : 'Today'}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span
                      className={`text-[11px] font-semibold px-3 py-1 rounded-full capitalize ${
                        r.processing_status === "completed" || r.processing_status === "analyzed"
                          ? "bg-teal-950/90 text-teal-300 border border-teal-500/40"
                          : r.processing_status === "failed"
                          ? "bg-rose-950/90 text-rose-300 border border-rose-800"
                          : "bg-amber-950/90 text-amber-300 border border-amber-800 animate-pulse"
                      }`}
                    >
                      {r.processing_status}
                    </span>

                    <button
                      onClick={(e) => handleDelete(e, r.report_id)}
                      className="p-2 rounded-xl text-slate-500 hover:text-rose-400 hover:bg-rose-950/40 border border-transparent hover:border-rose-900/40 transition-colors"
                      title="Permanently Delete Report"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>

                    <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-teal-400 group-hover:translate-x-0.5 transition-all" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <Disclaimer />
      </main>
    </div>
  );
}
