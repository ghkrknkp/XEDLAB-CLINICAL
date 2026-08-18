/**
 * localStore.js — localStorage-based report storage.
 * Used when the backend is unavailable. All data stays in the browser.
 */

const REPORTS_KEY = "mra_reports";
const FINDINGS_KEY = "mra_findings";
const SUMMARIES_KEY = "mra_summaries";
const PAGES_KEY = "mra_pages";
const STATUS_KEY = "mra_status";

function getStore(key) {
  try {
    return JSON.parse(localStorage.getItem(key) || "{}");
  } catch {
    return {};
  }
}

function setStore(key, data) {
  localStorage.setItem(key, JSON.stringify(data));
}

// ─── Reports ────────────────────────────────────────────────────────────────

export function saveReport(result) {
  const { report, findings, summary, pages } = result;
  const id = report.report_id;

  // Save report metadata
  const reports = getStore(REPORTS_KEY);
  reports[id] = report;
  setStore(REPORTS_KEY, reports);

  // Save findings
  const allFindings = getStore(FINDINGS_KEY);
  allFindings[id] = findings;
  setStore(FINDINGS_KEY, allFindings);

  // Save summary
  const allSummaries = getStore(SUMMARIES_KEY);
  allSummaries[id] = summary;
  setStore(SUMMARIES_KEY, allSummaries);

  // Save pages
  const allPages = getStore(PAGES_KEY);
  allPages[id] = pages;
  setStore(PAGES_KEY, allPages);

  // Mark completed
  const statuses = getStore(STATUS_KEY);
  statuses[id] = { status: "completed", stage: "COMPLETED", progress: 100 };
  setStore(STATUS_KEY, statuses);
}

export function getReport(reportId) {
  return getStore(REPORTS_KEY)[reportId] || null;
}

export function getAllReports() {
  const reports = getStore(REPORTS_KEY);
  return Object.values(reports).sort(
    (a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0)
  );
}

export function getFindings(reportId) {
  return getStore(FINDINGS_KEY)[reportId] || { findings: [], entities: [] };
}

export function getSummary(reportId) {
  return getStore(SUMMARIES_KEY)[reportId] || null;
}

export function getPages(reportId) {
  return getStore(PAGES_KEY)[reportId] || [];
}

export function getStatus(reportId) {
  return getStore(STATUS_KEY)[reportId] || null;
}

export function deleteReport(reportId) {
  [REPORTS_KEY, FINDINGS_KEY, SUMMARIES_KEY, PAGES_KEY, STATUS_KEY].forEach((key) => {
    const store = getStore(key);
    delete store[reportId];
    setStore(key, store);
  });
}

export function getComparisonTrends(reportId) {
  const reports = getStore(REPORTS_KEY);
  const allFindings = getStore(FINDINGS_KEY);
  const targetReport = reports[reportId];
  if (!targetReport) return {};

  const targetFindings = allFindings[reportId]?.findings || [];
  const targetTestNames = targetFindings.map((f) => f.test_name);

  const trends = {};
  targetTestNames.forEach((name) => {
    trends[name] = [];
  });

  // Collect data points from all reports that have matching tests
  Object.keys(reports).forEach((id) => {
    const rep = reports[id];
    const findings = allFindings[id]?.findings || [];
    findings.forEach((f) => {
      if (targetTestNames.includes(f.test_name)) {
        const val = parseFloat(f.value);
        if (!isNaN(val)) {
          trends[f.test_name].push({
            date: rep.created_at || new Date().toISOString(),
            value: val,
          });
        }
      }
    });
  });

  // Sort each test's data points chronologically
  Object.keys(trends).forEach((name) => {
    trends[name].sort((a, b) => new Date(a.date) - new Date(b.date));
    // Limit to only tests that have historical context (more than 1 data point) if too cluttered,
    // or return everything. Let's return everything.
  });

  return trends;
}

