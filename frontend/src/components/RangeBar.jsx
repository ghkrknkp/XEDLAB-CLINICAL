const STATUS_COLOR = {
  below_reference_range: "#c2793d",
  above_reference_range: "#c2793d",
  within_reference_range: "#0d8a99",
  unknown: "#94a3b8",
};

// The project's signature visual: a literal rendering of the deterministic
// range check (value vs. printed reference_low/reference_high) as a bar,
// so the one thing the app guarantees - grounded, auditable numeric
// comparison - is also the thing you see first.
export default function RangeBar({ value, low, high, status }) {
  if (low == null || high == null || value == null) {
    return <div className="h-1.5 w-full rounded-full bg-ink-900/10" title="Reference range not detected" />;
  }

  const span = high - low || 1;
  const padded = span * 0.25;
  const domainLow = low - padded;
  const domainHigh = high + padded;

  const pct = (v) => Math.min(100, Math.max(0, ((v - domainLow) / (domainHigh - domainLow)) * 100));

  const lowPct = pct(low);
  const highPct = pct(high);
  const valuePct = pct(value);
  const color = STATUS_COLOR[status] || STATUS_COLOR.unknown;

  return (
    <div className="relative h-4 w-full">
      <div className="absolute top-1/2 h-1.5 w-full -translate-y-1/2 rounded-full bg-ink-900/10" />
      <div
        className="absolute top-1/2 h-1.5 -translate-y-1/2 rounded-full bg-clinical-500/25"
        style={{ left: `${lowPct}%`, width: `${highPct - lowPct}%` }}
      />
      <div
        className="absolute top-1/2 h-3 w-3 -translate-y-1/2 -translate-x-1/2 rounded-full border-2 border-white shadow"
        style={{ left: `${valuePct}%`, backgroundColor: color }}
      />
    </div>
  );
}
