import {
  Chart as ChartJS, LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Legend);

const PALETTE = ["#0d8a99", "#c2793d", "#48566b", "#7c3aed", "#0891b2"];

export default function TrendChart({ trends }) {
  const testNames = Object.keys(trends || {});
  if (testNames.length === 0) {
    return <p className="text-sm text-ink-600">No historical data yet — upload and analyze more reports with matching test names to see trends.</p>;
  }

  const allDates = Array.from(
    new Set(testNames.flatMap((t) => trends[t].map((p) => p.date.slice(0, 10))))
  ).sort();

  const datasets = testNames.map((name, i) => {
    const byDate = Object.fromEntries(trends[name].map((p) => [p.date.slice(0, 10), p.value]));
    return {
      label: name,
      data: allDates.map((d) => byDate[d] ?? null),
      borderColor: PALETTE[i % PALETTE.length],
      backgroundColor: PALETTE[i % PALETTE.length],
      spanGaps: true,
      tension: 0.25,
    };
  });

  return (
    <div className="rounded-xl border border-ink-900/10 bg-white p-4">
      <div className="mb-3 font-mono text-xs uppercase tracking-wide text-ink-600">
        Historical report comparison
      </div>
      <Line
        data={{ labels: allDates, datasets }}
        options={{
          responsive: true,
          plugins: { legend: { position: "bottom" } },
          scales: { y: { beginAtZero: false } },
        }}
      />
    </div>
  );
}
