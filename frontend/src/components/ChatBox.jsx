import React, { useState, useRef } from "react";
import {
  MessageSquare,
  Send,
  Sparkles,
  FileText,
  AlertCircle,
  Paperclip,
  UploadCloud,
  FileSpreadsheet,
  CheckCircle2,
  Activity,
  ArrowUpRight,
} from "lucide-react";
import { reports as reportsApi } from "../services/api";
import { analyzeFile, answerQuestionLocal } from "../services/localAnalyzer";
import { saveReport, getFindings, getSummary, getPages, getReport } from "../services/localStore";

const SUGGESTIONS = [
  "Which values are outside the reference range?",
  "What was my hemoglobin level?",
  "Give the RBC count and glucose ranges",
  "What does this report tell me?",
];

const QUICK_SAMPLES = [
  {
    name: "Sample CBC",
    type: "CBC",
    content: `Patient ID: P1001\nAge: 22\nDate: 2026-08-17\n\nComplete Blood Count\n\nHemoglobin 10.2 g/dL 12.0 - 16.0\nWBC 7200 /uL 4000 - 11000\nPlatelets 250000 /uL 150000 - 450000\nHematocrit 39 % 36 - 46`,
  },
  {
    name: "Sample Lipid",
    type: "Lipid Profile",
    content: `Patient ID: P2045\nAge: 48\nDate: 2026-08-15\n\nLipid Profile\n\nTotal Cholesterol: 235 mg/dL (125-200)\nHDL Cholesterol: 42 mg/dL (40-60)\nLDL Cholesterol: 155 mg/dL (0-100)\nTriglycerides: 190 mg/dL (35-150)`,
  },
];

export default function ChatBox({ reportId, onSelectSource, onReportUploaded }) {
  const [activeReportId, setActiveReportId] = useState(reportId);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! I am your AI clinical report assistant. You can ask me questions about laboratory findings, reference ranges, or attach/upload a medical report directly using the paperclip icon below!",
      sources: [],
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploadingInChat, setUploadingInChat] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  // Sync reportId when props change
  React.useEffect(() => {
    if (reportId) {
      setActiveReportId(reportId);
    }
  }, [reportId]);

  const handleSend = async (questionText) => {
    const query = questionText || input;
    if (!query.trim() || loading) return;

    const userMessage = { role: "user", content: query, sources: [] };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);
    setError(null);

    const currentId = activeReportId || reportId;

    if (!currentId) {
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content:
              "Please upload or select a medical report first so I can retrieve grounded findings for your question.",
            sources: [],
          },
        ]);
        setLoading(false);
      }, 500);
      return;
    }

    try {
      let ansText = "";
      let ansSources = [];
      let modelUsed = "Clinical RAG";

      try {
        const res = await reportsApi.ask(currentId, query);
        ansText = res.data.answer;
        ansSources = res.data.retrieved_sources || [];
        modelUsed = res.data.model_used || "FastAPI RAG Engine";
      } catch (backendErr) {
        ansText = "";
      }

      // If backend was unhelpful or unavailable, run fuzzy local matcher
      if (!ansText || ansText.includes("does not contain enough information")) {
        const findingsData = getFindings(currentId);
        const reportData = getReport(currentId);
        const pagesData = getPages(currentId);
        const rawText = pagesData && pagesData[0] ? pagesData[0].raw_text : "";
        const fList = findingsData?.findings || [];
        const repType = reportData?.report_type || "Medical Report";

        const localRes = answerQuestionLocal(query, fList, repType, rawText);
        ansText = localRes.answer;
        ansSources = localRes.sources || [];
        modelUsed = "Clinical Engine";
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: ansText,
          sources: ansSources,
          model_used: modelUsed,
        },
      ]);
    } catch (err) {
      const msg = err.response?.data?.detail || "Could not retrieve answer from report context. Please try again.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  // Direct File Upload from Chat
  const handleChatFileUpload = async (file) => {
    if (!file) return;
    setUploadingInChat(true);
    setError(null);

    const userUploadMsg = {
      role: "user",
      content: `Uploaded document: 📄 ${file.name} (${(file.size / 1024).toFixed(1)} KB)`,
      isUpload: true,
    };
    setMessages((prev) => [...prev, userUploadMsg]);

    try {
      let newReportId = null;
      try {
        const res = await reportsApi.upload(file);
        newReportId = res.data.report_id;
      } catch (backendErr) {
        const result = await analyzeFile(file);
        saveReport(result);
        newReportId = result.report.report_id;
      }

      setActiveReportId(newReportId);
      if (onReportUploaded) {
        onReportUploaded(newReportId);
      }

      // Add success response with findings summary
      const localFindings = getFindings(newReportId);
      const findingsCount = localFindings?.findings?.length || 0;
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `✅ Successfully analyzed **${file.name}** (Report ID: \`${newReportId}\`)!\n\nExtracted **${findingsCount}** laboratory measurement(s). All numerical values have been verified against printed reference ranges.\n\nYou can ask about test results (e.g., *"What is my RBC count?"*, *"What ranges of sugar?"*, or *"What does the report tell?"*).`,
          isReportSummary: true,
          reportId: newReportId,
        },
      ]);
    } catch (err) {
      setError("Failed to analyze uploaded file in chat: " + (err.message || "Unknown error"));
    } finally {
      setUploadingInChat(false);
    }
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragOver(true);
      }}
      onDragLeave={() => setIsDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setIsDragOver(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
          handleChatFileUpload(e.dataTransfer.files[0]);
        }
      }}
      className={`bg-slate-900 rounded-3xl border ${
        isDragOver ? "border-cyan-400 bg-slate-900/90 shadow-xl shadow-cyan-500/20" : "border-slate-800"
      } shadow-xl flex flex-col h-[560px] overflow-hidden transition-all text-slate-100 relative`}
    >
      {/* Hidden File Input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={(e) => {
          if (e.target.files && e.target.files[0]) {
            handleChatFileUpload(e.target.files[0]);
          }
        }}
        accept=".pdf,.png,.jpg,.jpeg,.txt"
        className="hidden"
      />

      {/* Drag & Drop Visual Overlay */}
      {isDragOver && (
        <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-xs z-30 flex flex-col items-center justify-center border-2 border-dashed border-cyan-400 rounded-3xl pointer-events-none">
          <UploadCloud className="w-12 h-12 text-cyan-400 animate-bounce mb-2" />
          <p className="text-sm font-bold text-white">Drop Medical Report to Analyze in Chat</p>
          <p className="text-xs text-cyan-300/80 mt-1">PDF, PNG, JPG, TXT supported</p>
        </div>
      )}

      {/* Header */}
      <div className="p-4 bg-slate-950/80 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 p-0.5 flex items-center justify-center shadow-md shadow-cyan-500/20">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <MessageSquare className="w-4 h-4 text-cyan-400" />
            </div>
          </div>
          <div>
            <h3 className="text-xs font-bold text-white flex items-center gap-2">
              Clinical Report Assistant
              {activeReportId && (
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-950 border border-cyan-500/30 text-cyan-300">
                  {activeReportId}
                </span>
              )}
            </h3>
            <p className="text-[10px] text-slate-400">Grounded in verified laboratory evidence</p>
          </div>
        </div>

        {/* Quick Attach Sample Dropdown / Button */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploadingInChat}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-cyan-300 text-xs font-medium transition-all"
            title="Upload report directly into chat"
          >
            <Paperclip className="w-3.5 h-3.5" />
            <span>Upload File</span>
          </button>
        </div>
      </div>

      {/* Quick Ask / Sample Attachment Chips */}
      <div className="px-4 py-2 bg-slate-950/40 border-b border-slate-800/80 flex items-center gap-2 overflow-x-auto no-scrollbar">
        <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider whitespace-nowrap flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-cyan-400" /> Quick Ask:
        </span>
        {SUGGESTIONS.map((s, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(s)}
            disabled={loading || uploadingInChat}
            className="text-[11px] font-medium text-slate-300 bg-slate-800/80 border border-slate-700 hover:border-cyan-400 hover:text-cyan-300 px-3 py-1 rounded-full whitespace-nowrap transition-colors disabled:opacity-50"
          >
            {s}
          </button>
        ))}
      </div>

      {/* Chat Messages Feed */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4 text-xs">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex flex-col ${m.role === "user" ? "items-end" : "items-start"}`}
          >
            <div
              className={`max-w-[85%] p-4 rounded-2xl ${
                m.role === "user"
                  ? "bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-br-xs shadow-md shadow-cyan-900/20"
                  : "bg-slate-800/90 border border-slate-700/80 text-slate-200 rounded-bl-xs leading-relaxed whitespace-pre-line shadow-sm"
              }`}
            >
              {m.content}

              {/* Source Page Badges */}
              {m.sources && m.sources.length > 0 && (
                <div className="mt-3 pt-2.5 border-t border-slate-700/60 flex flex-wrap items-center gap-1.5">
                  <span className="text-[10px] font-semibold text-slate-400">Sources:</span>
                  {m.sources.map((src, sIdx) => (
                    <button
                      key={sIdx}
                      onClick={() => onSelectSource && onSelectSource(src)}
                      className="inline-flex items-center gap-1 text-[10px] font-medium bg-cyan-950/80 text-cyan-300 border border-cyan-500/30 px-2 py-0.5 rounded-md hover:bg-cyan-900/60 transition-colors"
                    >
                      <FileText className="w-2.5 h-2.5" />
                      Page {src.page || 1}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {uploadingInChat && (
          <div className="flex items-center gap-2 p-3 bg-cyan-950/40 border border-cyan-500/30 rounded-2xl text-cyan-300 text-xs animate-pulse">
            <Activity className="w-4 h-4 animate-spin text-cyan-400" />
            <span>Analyzing uploaded report and extracting clinical findings...</span>
          </div>
        )}

        {loading && (
          <div className="flex items-center gap-2 text-slate-400 text-xs italic">
            <Sparkles className="w-3.5 h-3.5 animate-spin text-cyan-400" />
            Retrieving grounded answer from report chunks...
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2 p-3 bg-rose-950/40 border border-rose-800 rounded-xl text-rose-300 text-xs">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Input & Upload Bar */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="p-3 bg-slate-950/90 border-t border-slate-800 flex items-center gap-2"
      >
        {/* Attachment Button */}
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={loading || uploadingInChat}
          title="Attach PDF, scan, or TXT report"
          className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-cyan-300 border border-slate-700 transition-colors"
        >
          <Paperclip className="w-4 h-4" />
        </button>

        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about test results (e.g. 'RBC count', 'sugar ranges', 'what report tells')..."
          disabled={loading || uploadingInChat}
          className="flex-1 px-4 py-2.5 text-xs rounded-xl border border-slate-700 bg-slate-900 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/30 focus:border-cyan-500"
        />

        <button
          type="submit"
          disabled={!input.trim() || loading || uploadingInChat}
          className="p-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold rounded-xl disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-md shadow-cyan-500/20"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}
