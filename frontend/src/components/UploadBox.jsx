import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import { reports } from "../services/api";

const ACCEPTED = [".pdf", ".png", ".jpg", ".jpeg", ".txt"];

export default function UploadBox() {
  const [dragging, setDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState(""); // "", "uploading", "analyzing", "error"
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const validate = (f) => {
    const ext = "." + f.name.split(".").pop().toLowerCase();
    if (!ACCEPTED.includes(ext)) return `Unsupported file type ${ext}. Use PDF, PNG, JPG, or TXT.`;
    if (f.size > 10 * 1024 * 1024) return "File exceeds the 10 MB limit.";
    return null;
  };

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files?.[0];
    if (f) handleFile(f);
  }, []);

  const handleFile = (f) => {
    const err = validate(f);
    if (err) {
      setError(err);
      setFile(null);
      return;
    }
    setError("");
    setFile(f);
  };

  const runAnalysis = async () => {
    if (!file) return;
    try {
      setStatus("uploading");
      const uploadResp = await reports.upload(file);
      const reportId = uploadResp.data.report_id;

      setStatus("analyzing");
      await reports.analyze(reportId);

      navigate(`/reports/${reportId}`);
    } catch (e) {
      setStatus("error");
      setError(e?.response?.data?.detail || "Something went wrong analyzing this report.");
    }
  };

  return (
    <div>
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={`flex flex-col items-center justify-center rounded-xl border-2 border-dashed px-8 py-16 text-center transition-colors ${
          dragging ? "border-clinical-500 bg-clinical-50" : "border-ink-900/15 bg-white"
        }`}
      >
        <div className="mb-3 font-mono text-xs uppercase tracking-widest text-ink-600">
          PDF · PNG · JPG · TXT — up to 10 MB
        </div>
        <p className="mb-5 text-ink-800">Drop a medical report here, or choose a file</p>
        <label className="cursor-pointer rounded-md bg-ink-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-ink-800">
          Choose file
          <input
            type="file"
            className="hidden"
            accept={ACCEPTED.join(",")}
            onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
          />
        </label>

        {file && (
          <div className="mt-6 flex items-center gap-3 rounded-md border border-ink-900/10 bg-ink-900/[0.03] px-4 py-2 font-mono text-sm">
            <span>{file.name}</span>
            <span className="text-ink-600">{(file.size / 1024).toFixed(0)} KB</span>
          </div>
        )}

        {error && <div className="mt-4 text-sm text-red-600">{error}</div>}
      </div>

      <div className="mt-5 flex justify-end">
        <button
          disabled={!file || status === "uploading" || status === "analyzing"}
          onClick={runAnalysis}
          className="rounded-md bg-clinical-500 px-6 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-clinical-600 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {status === "uploading" && "Uploading…"}
          {status === "analyzing" && "Analyzing report…"}
          {(status === "" || status === "error") && "Analyze report"}
        </button>
      </div>
    </div>
  );
}
