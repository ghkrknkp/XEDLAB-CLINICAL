import { useState } from "react";
import { reports } from "../services/api";

export default function AskPanel({ reportId }) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]); // {role, text, sources}
  const [loading, setLoading] = useState(false);

  const ask = async (e) => {
    e.preventDefault();
    if (!question.trim() || loading) return;
    const q = question.trim();
    setMessages((m) => [...m, { role: "user", text: q }]);
    setQuestion("");
    setLoading(true);
    try {
      const resp = await reports.ask(reportId, q);
      setMessages((m) => [...m, { role: "assistant", text: resp.data.answer, sources: resp.data.retrieved_sources }]);
    } catch (err) {
      setMessages((m) => [...m, { role: "assistant", text: "Sorry, I couldn't answer that. Please try again.", sources: [] }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-full flex-col rounded-xl border border-ink-900/10 bg-white">
      <div className="border-b border-ink-900/10 px-4 py-3">
        <div className="font-mono text-xs uppercase tracking-wide text-ink-600">Ask about this report</div>
      </div>

      <div className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
        {messages.length === 0 && (
          <p className="text-sm text-ink-600">
            Try: "Which values are outside the reference range?" or "What was my glucose value?"
          </p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={m.role === "user" ? "text-right" : ""}>
            <div
              className={`inline-block max-w-[90%] whitespace-pre-wrap rounded-lg px-3 py-2 text-left text-sm ${
                m.role === "user" ? "bg-ink-900 text-white" : "bg-ink-900/[0.04] text-ink-800"
              }`}
            >
              {m.text}
            </div>
            {m.sources?.length > 0 && (
              <div className="mt-1 space-y-1 text-left">
                {m.sources.map((s, j) => (
                  <div key={j} className="font-mono text-[11px] text-ink-600">
                    Page {s.page} — {s.text.slice(0, 100)}{s.text.length > 100 ? "…" : ""}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && <div className="text-sm text-ink-600">Thinking…</div>}
      </div>

      <form onSubmit={ask} className="flex gap-2 border-t border-ink-900/10 p-3">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about this report…"
          className="flex-1 rounded-md border border-ink-900/15 px-3 py-2 text-sm focus:border-clinical-500 focus:outline-none"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-clinical-500 px-4 py-2 text-sm font-semibold text-white hover:bg-clinical-600 disabled:opacity-40"
        >
          Ask
        </button>
      </form>
    </div>
  );
}
