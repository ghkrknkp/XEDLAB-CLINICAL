import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import SummaryCard from "../components/SummaryCard";
import FindingsTable from "../components/FindingsTable";
import SourceViewer from "../components/SourceViewer";
import ChatBox from "../components/ChatBox";
import TrendChart from "../components/TrendChart";
import ProcessingStatus from "../components/ProcessingStatus";
import Disclaimer from "../components/Disclaimer";
import { reports as reportsApi } from "../services/api";
import { getReport, getFindings, getSummary, getPages, deleteReport, getComparisonTrends } from "../services/localStore";
import {
  FileText,
  Table,
  Eye,
  MessageSquare,
  TrendingUp,
  Trash2,
  ArrowLeft,
  Calendar,
  Sparkles,
  AlertCircle,
  Activity,
  CheckCircle2,
} from "lucide-react";

export default function ReportView() {
  const { reportId } = useParams();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState("findings"); // findings | summary | source | qa | trends
  const [report, setReport] = useState(null);
  const [summaryData, setSummaryData] = useState(null);
  const [findingsData, setFindingsData] = useState({ findings: [], entities: [] });
  const [pages, setPages] = useState([]);
  const [trends, setTrends] = useState({});
  const [loading, setLoading] = useState(true);
  const [highlightedSnippet, setHighlightedSnippet] = useState("");
  const [deleteConfirm, setDeleteConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const fetchAllData = async () => {
    try {
      const [repRes, sumRes, findRes, pagRes, trRes] = await Promise.all([
        reportsApi.get(reportId),
        reportsApi.summary(reportId).catch(() => ({ data: null })),
        reportsApi.findings(reportId).catch(() => ({ data: { findings: [], entities: [] } })),
        reportsApi.pages(reportId).catch(() => ({ data: [] })),
        reportsApi.comparison(reportId).catch(() => ({ data: { trends: {} } })),
      ]);

      setReport(repRes.data);
      setSummaryData(sumRes.data);
      setFindingsData(findRes.data);
      setPages(pagRes.data);
      setTrends(trRes.data?.trends || {});
    } catch (err) {
      const localReport = getReport(reportId);
      if (localReport) {
        setReport(localReport);
        setSummaryData(getSummary(reportId));
        setFindingsData(getFindings(reportId) || { findings: [], entities: [] });
        setPages(getPages(reportId) || []);
        setTrends(getComparisonTrends(reportId) || {});
      } else {
        console.error(err);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, [reportId]);

  const handleSelectSource = (sourceInfo) => {
    if (sourceInfo && sourceInfo.text) {
      setHighlightedSnippet(sourceInfo.text);
      setActiveTab("source");
    }
  };

  const handleDelete = async () => {
    setDeleting(true);
    try {
      try {
        await reportsApi.remove(reportId);
      } catch (err) {}
      deleteReport(reportId);
      navigate("/history");
    } catch (err) {
      alert("Failed to delete report. Please try again.");
    } finally {
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen bg-slate-950 text-slate-100 font-sans">
        <Sidebar />
        <main className="flex-1 p-10 flex items-center justify-center">
          <div className="text-center">
            <Sparkles className="w-8 h-8 text-teal-400 animate-spin mx-auto mb-3" />
            <p className="text-xs text-slate-400">Loading clinical report analysis...</p>
          </div>
        </main>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="flex min-h-screen bg-slate-950 text-slate-100 font-sans">
        <Sidebar />
        <main className="flex-1 p-10 max-w-4xl mx-auto">
          <div className="p-8 bg-slate-900 border border-slate-800 rounded-3xl text-center">
            <AlertCircle className="w-10 h-10 text-rose-400 mx-auto mb-3" />
            <h2 className="text-lg font-bold text-white">Report Not Found</h2>
            <p className="text-xs text-slate-400 mt-1 mb-6">
              The requested report ID `{reportId}` does not exist or has been removed.
            </p>
            <button
              onClick={() => navigate("/dashboard")}
              className="px-5 py-2.5 bg-teal-500 hover:bg-teal-400 text-slate-950 text-xs font-bold rounded-xl transition-colors"
            >
              Back to Dashboard
            </button>
          </div>
        </main>
      </div>
    );
  }

  const isProcessing =
    report.processing_status === "queued" || report.processing_status === "processing";

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 font-sans">
      <Sidebar />

      <main className="flex-1 p-6 sm:p-10 max-w-6xl mx-auto">
        {/* Navigation & Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate("/dashboard")}
            className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-teal-300 transition-colors mb-4"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Dashboard
          </button>

          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1.5">
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono bg-teal-950 border border-teal-500/40 text-teal-300">
                  {report.report_id}
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-slate-900 border border-slate-800 text-slate-300">
                  {report.report_type}
                </span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                {report.filename}
              </h1>
              <div className="flex items-center gap-3 text-xs text-slate-400 mt-1.5 font-light">
                <span className="flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5 text-teal-400" />
                  {report.created_at ? new Date(report.created_at).toLocaleDateString() : 'Today'}
                </span>
                <span>•</span>
                <span>{report.page_count} Page(s)</span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
              {deleteConfirm ? (
                <div className="flex items-center gap-2 bg-rose-950/80 border border-rose-800 p-1.5 rounded-xl">
                  <span className="text-[11px] text-rose-300 font-semibold px-2">Confirm Delete?</span>
                  <button
                    onClick={handleDelete}
                    disabled={deleting}
                    className="px-3 py-1 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-bold"
                  >
                    {deleting ? "Deleting..." : "Yes, Delete"}
                  </button>
                  <button
                    onClick={() => setDeleteConfirm(false)}
                    className="px-3 py-1 bg-slate-800 text-slate-300 rounded-lg text-xs"
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setDeleteConfirm(true)}
                  className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-rose-400 hover:border-rose-900 transition-colors"
                  title="Delete Report"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Live Status if Processing */}
        {isProcessing && (
          <div className="mb-8">
            <ProcessingStatus reportId={reportId} onComplete={fetchAllData} />
          </div>
        )}

        {/* Calm Navigation Tabs */}
        <div className="flex items-center gap-1.5 border-b border-slate-800 mb-8 overflow-x-auto no-scrollbar pb-1">
          {[
            { id: "findings", label: "Structured Findings", icon: Table },
            { id: "summary", label: "Patient Summary", icon: FileText },
            { id: "qa", label: "Report Q&A Chat", icon: MessageSquare },
            { id: "source", label: "Extracted Source", icon: Eye },
            { id: "trends", label: "Trend Comparison", icon: TrendingUp },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2.5 text-xs font-bold rounded-t-xl transition-all border-b-2 whitespace-nowrap ${
                  isActive
                    ? "border-teal-400 text-teal-300 bg-slate-900/80"
                    : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-teal-400" : "text-slate-400"}`} />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Tab Content Panes */}
        <div className="space-y-8">
          {activeTab === "findings" && (
            <FindingsTable
              findings={findingsData.findings}
              entities={findingsData.entities}
            />
          )}

          {activeTab === "summary" && (
            <SummaryCard
              summary={summaryData?.summary}
              disclaimer={summaryData?.disclaimer}
              modelUsed={summaryData?.summary_source}
            />
          )}

          {activeTab === "qa" && (
            <ChatBox
              reportId={reportId}
              onSelectSource={handleSelectSource}
            />
          )}

          {activeTab === "source" && (
            <SourceViewer
              pages={pages}
              highlightSnippet={highlightedSnippet}
            />
          )}

          {activeTab === "trends" && (
            <TrendChart trends={trends} />
          )}
        </div>

        {/* Mandatory Safety Disclaimer */}
        <div className="mt-12">
          <Disclaimer />
        </div>
      </main>
    </div>
  );
}
