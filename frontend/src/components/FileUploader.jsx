import React, { useState, useRef } from "react";
import { Upload, FileText, CheckCircle2, AlertCircle, Sparkles, FileSpreadsheet, ArrowRight, RefreshCw, Server } from "lucide-react";
import { reports as reportsApi } from "../services/api";
import { analyzeFile } from "../services/localAnalyzer";
import { saveReport } from "../services/localStore";

const SAMPLE_REPORTS = [
  {
    name: "Sample CBC Report (Complete Blood Count)",
    filename: "sample_cbc.txt",
    type: "CBC",
    content: `Patient ID: P1001\nAge: 22\nDate: 2026-08-17\n\nComplete Blood Count\n\nHemoglobin 10.2 g/dL 12.0 - 16.0\nWBC 7200 /uL 4000 - 11000\nPlatelets 250000 /uL 150000 - 450000\nHematocrit 39 % 36 - 46`,
  },
  {
    name: "Sample Lipid Profile (Cholesterol Panel)",
    filename: "sample_lipid.txt",
    type: "Lipid Profile",
    content: `Patient ID: P2045\nAge: 48\nGender: Male\nDate: 2026-08-15\n\nLipid Profile Panel\n\nTotal Cholesterol: 235 mg/dL (125-200)\nHDL Cholesterol: 42 mg/dL (40-60)\nLDL Cholesterol: 155 mg/dL (0-100)\nTriglycerides: 190 mg/dL (35-150)\nVLDL: 38 mg/dL (5-30)`,
  },
  {
    name: "Sample Liver Function Test (LFT)",
    filename: "sample_lft.txt",
    type: "Liver Function Test",
    content: `Patient ID: P3188\nAge: 35\nGender: Female\nDate: 2026-08-10\n\nLiver Function Test (LFT)\n\nTotal Bilirubin 0.8 mg/dL 0.2 - 1.2\nDirect Bilirubin 0.2 mg/dL 0.0 - 0.3\nSGOT (AST) 28 U/L 10 - 40\nSGPT (ALT) 32 U/L 7 - 56\nAlkaline Phosphatase 85 U/L 44 - 147\nTotal Protein 7.1 g/dL 6.0 - 8.3\nAlbumin 4.3 g/dL 3.5 - 5.0`,
  },
];

export default function FileUploader({ onUploadSuccess }) {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [isOcrHint, setIsOcrHint] = useState(false);
  const fileInputRef = useRef(null);

  const validateFile = (selectedFile) => {
    const validExtensions = [".pdf", ".png", ".jpg", ".jpeg", ".txt"];
    const ext = "." + selectedFile.name.split(".").pop().toLowerCase();

    if (!validExtensions.includes(ext)) {
      setError(`Unsupported file type '${ext}'. Please upload PDF, PNG, JPG, or TXT.`);
      setIsOcrHint(false);
      return false;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setError("File exceeds maximum allowed size of 10 MB.");
      setIsOcrHint(false);
      return false;
    }

    setError(null);
    setIsOcrHint(false);
    return true;
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      if (validateFile(selected)) {
        setFile(selected);
      }
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const selected = e.dataTransfer.files[0];
      if (validateFile(selected)) {
        setFile(selected);
      }
    }
  };

  const uploadSelectedFile = async (fileToUpload) => {
    if (!fileToUpload) return;
    setUploading(true);
    setProgress(15);
    setError(null);
    setIsOcrHint(false);

    try {
      // 1. Try Backend Upload First (Tesseract OCR Engine)
      const res = await reportsApi.upload(fileToUpload, (evt) => {
        if (evt.total) {
          const pct = Math.round((evt.loaded * 85) / evt.total);
          setProgress(pct);
        }
      });
      setProgress(100);
      setUploading(false);
      setFile(null);
      if (onUploadSuccess) {
        onUploadSuccess(res.data);
      }
    } catch (err) {
      console.warn("Backend upload failed, attempting client-side analysis:", err);
      // 2. Client-side Fallback
      try {
        setProgress(50);
        const result = await analyzeFile(fileToUpload);
        setProgress(100);
        saveReport(result);
        setUploading(false);
        setFile(null);
        if (onUploadSuccess) {
          onUploadSuccess({ report_id: result.report.report_id, job_id: 'local', status: 'completed' });
        }
      } catch (localErr) {
        setUploading(false);
        const isImage = [".jpg", ".jpeg", ".png", ".pdf"].some((ext) => fileToUpload.name.toLowerCase().endsWith(ext));
        if (isImage) {
          setIsOcrHint(true);
          setError(
            `Scanned images and PDFs require the backend OCR engine (http://localhost:8000). ` +
            `Please ensure your backend server is running with 'venv312\\Scripts\\python.exe -m uvicorn app.main:app --reload' or test with sample text reports.`
          );
        } else {
          setError(localErr.message || "Failed to analyze document.");
        }
      }
    }
  };

  const handleSampleLoad = (sample) => {
    const blob = new Blob([sample.content], { type: "text/plain" });
    const sampleFile = new File([blob], sample.filename, { type: "text/plain" });
    setFile(sampleFile);
    uploadSelectedFile(sampleFile);
  };

  return (
    <div className="bg-slate-900/90 backdrop-blur-xl border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-xl text-slate-100">
      <div className="text-center max-w-lg mx-auto mb-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-950/80 border border-teal-500/30 text-teal-300 text-xs font-semibold mb-3 shadow-inner">
          <Sparkles className="w-3.5 h-3.5 text-teal-400" />
          Calm Modern Medical Intelligence
        </div>
        <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
          Upload Medical Report
        </h2>
        <p className="text-xs text-slate-400 mt-1.5 font-light">
          Supports standard PDF documents, scanned images (PNG, JPG, JPEG), and laboratory text reports up to 10 MB.
        </p>
      </div>

      {/* Drop Zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => !uploading && fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-2xl p-8 text-center transition-all cursor-pointer ${
          isDragging
            ? "border-teal-400 bg-teal-950/20 scale-[0.99] shadow-lg shadow-teal-500/10"
            : "border-slate-700/80 hover:border-teal-500/60 bg-slate-950/50 hover:bg-slate-950/80"
        } ${uploading ? "opacity-60 pointer-events-none" : ""}`}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".pdf,.png,.jpg,.jpeg,.txt"
          className="hidden"
        />

        <div className="w-14 h-14 rounded-2xl bg-teal-950/80 border border-teal-500/30 text-teal-400 flex items-center justify-center mx-auto mb-3.5 shadow-md">
          <Upload className="w-6 h-6" />
        </div>

        {file ? (
          <div>
            <span className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-medium bg-teal-950 border border-teal-500/40 text-teal-300 shadow-sm">
              <FileText className="w-4 h-4 text-teal-400" />
              {file.name} ({(file.size / 1024).toFixed(1)} KB)
            </span>
            <p className="text-xs text-slate-400 mt-2.5">Click or drag another file to replace</p>
          </div>
        ) : (
          <div>
            <p className="text-sm font-semibold text-slate-200">
              Drag & drop your report here, or <span className="text-teal-400 underline decoration-teal-500/40 underline-offset-4">browse files</span>
            </p>
            <p className="text-xs text-slate-400 mt-1 font-light">PDF, JPG, PNG, TXT (Maximum 10 MB)</p>
          </div>
        )}

        {/* Progress Bar */}
        {uploading && (
          <div className="mt-5 max-w-xs mx-auto">
            <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden p-0.5 border border-slate-700">
              <div
                className="bg-gradient-to-r from-teal-500 to-cyan-400 h-full transition-all duration-300 rounded-full shadow-sm"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-[11px] text-teal-300 mt-2 font-medium">Processing Document: {progress}%</p>
          </div>
        )}
      </div>

      {/* Friendly Error Banner with OCR Instructions */}
      {error && (
        <div className="mt-4 p-4 bg-slate-950 border border-amber-500/30 rounded-2xl text-xs space-y-3">
          <div className="flex items-start gap-2.5 text-amber-300">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <p className="leading-relaxed">{error}</p>
          </div>

          {isOcrHint && (
            <div className="pt-2 border-t border-slate-800 flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
                <Server className="w-3.5 h-3.5 text-teal-400" />
                <span>Backend OCR Command: <code className="bg-slate-900 px-1.5 py-0.5 rounded text-teal-300 font-mono">python -m uvicorn app.main:app --reload</code></span>
              </div>
              <button
                onClick={(e) => { e.stopPropagation(); uploadSelectedFile(file); }}
                className="px-3 py-1 bg-teal-500/20 hover:bg-teal-500/30 text-teal-300 border border-teal-500/40 rounded-xl font-semibold text-[11px] transition-colors inline-flex items-center gap-1"
              >
                <RefreshCw className="w-3 h-3" /> Retry with Backend
              </button>
            </div>
          )}
        </div>
      )}

      {/* Manual Upload Action */}
      {file && !uploading && (
        <div className="mt-5 text-center">
          <button
            onClick={(e) => { e.stopPropagation(); uploadSelectedFile(file); }}
            className="px-7 py-3 bg-gradient-to-r from-teal-500 to-cyan-500 hover:from-teal-400 hover:to-cyan-400 text-slate-950 font-bold text-xs rounded-xl shadow-lg shadow-teal-500/20 transition-all inline-flex items-center gap-2"
          >
            Start Analysis <ArrowRight className="w-4 h-4 text-slate-950" />
          </button>
        </div>
      )}

      {/* Quick Sample Reports Section */}
      <div className="mt-8 pt-6 border-t border-slate-800">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Or test instantly with sample reports
          </span>
          <span className="text-[11px] text-teal-400 font-medium flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3 text-teal-400" /> 1-Click Instant Test
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {SAMPLE_REPORTS.map((sample, idx) => (
            <button
              key={idx}
              onClick={() => handleSampleLoad(sample)}
              disabled={uploading}
              className="flex items-start gap-3 p-3.5 rounded-2xl border border-slate-800 hover:border-teal-500/50 bg-slate-950/60 hover:bg-teal-950/20 text-left transition-all group"
            >
              <div className="w-8 h-8 rounded-xl bg-teal-950/80 border border-teal-500/30 text-teal-400 flex items-center justify-center flex-shrink-0 mt-0.5">
                <FileSpreadsheet className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-slate-200 group-hover:text-teal-300 transition-colors">
                  {sample.type}
                </h4>
                <p className="text-[11px] text-slate-400 truncate max-w-[150px]">{sample.name}</p>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
