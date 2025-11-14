"use client";

import { useState } from "react";

export default function ReportsPage() {
  const [customRange, setCustomRange] = useState(false);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [exporting, setExporting] = useState(false);
  const [exportStatus, setExportStatus] = useState<{
    type: string;
    format: string;
  } | null>(null);

  const handleExport = async (
    status: string | null,
    days: number | null,
    format: "csv" | "json",
    customStart?: string,
    customEnd?: string
  ) => {
    try {
      setExporting(true);
      setExportStatus({ type: status || "all", format });
      const params = new URLSearchParams();
      params.append("format", format);

      if (status) {
        params.append("status", status);
      }

      if (days) {
        // For days-based queries, set end date to end of today
        const end = new Date();
        end.setHours(23, 59, 59, 999);
        const start = new Date();
        start.setDate(start.getDate() - days);
        start.setHours(0, 0, 0, 0);
        params.append("startDate", start.toISOString().split("T")[0]);
        params.append("endDate", end.toISOString().split("T")[0]);
      } else if (customStart && customEnd) {
        // For custom range, set start to beginning of day and end to end of day
        const start = new Date(customStart);
        start.setHours(0, 0, 0, 0);
        const end = new Date(customEnd);
        end.setHours(23, 59, 59, 999);
        params.append("startDate", start.toISOString());
        params.append("endDate", end.toISOString());
      }

      const response = await fetch(`/api/reports/export?${params.toString()}`);
      if (response.ok) {
        // Check if response is JSON or CSV
        const contentType = response.headers.get("content-type");
        if (contentType?.includes("application/json")) {
          const data = await response.json();
          const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          const filename = `submission-logs-${new Date().toISOString().split("T")[0]}.${format}`;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
        } else {
          // CSV or other text format
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          const filename = response.headers
            .get("content-disposition")
            ?.split("filename=")[1]
            ?.replace(/"/g, "") || `submission-logs-${new Date().toISOString().split("T")[0]}.${format}`;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
        }
        setExportStatus(null);
      } else {
        const error = await response.json().catch(() => ({ detail: "Failed to export logs" }));
        alert(error.detail || "Failed to export logs");
        setExportStatus(null);
      }
    } catch (error) {
      console.error("Failed to export:", error);
      alert("Failed to export logs. Please try again.");
      setExportStatus(null);
    } finally {
      setExporting(false);
    }
  };

  const handleTodaySuccess = () => handleExport("success", 1, "csv");
  const handleWeekFailed = () => handleExport("failed", 7, "json");
  const handleCustomExport = () => {
    if (!startDate || !endDate) {
      alert("Please select both start and end dates");
      return;
    }
    if (new Date(startDate) > new Date(endDate)) {
      alert("Start date must be before end date");
      return;
    }
    handleExport(null, null, "csv", startDate, endDate);
  };

  const getButtonText = (baseText: string, format: string, type: string) => {
    if (
      exporting &&
      exportStatus?.type === type &&
      exportStatus?.format === format
    ) {
      return "Exporting...";
    }
    return baseText;
  };

  return (
    <div className="space-y-6">
      <header>
        <h2 className="text-2xl font-semibold text-white">Reports & Exports</h2>
        <p className="text-sm text-slate-400">
          Generate on-demand analytics or schedule exports for stakeholders.
        </p>
      </header>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <h3 className="text-lg font-semibold text-white">Quick Exports</h3>
          <p className="mt-2 text-xs text-slate-400">Choose presets to export recent automation data.</p>
          <div className="mt-4 grid gap-3">
            <button
              onClick={handleTodaySuccess}
              disabled={exporting}
              className="rounded-lg bg-indigo-500 px-4 py-2 text-xs font-medium text-white hover:bg-indigo-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {getButtonText("Success Today (CSV)", "csv", "success")}
            </button>
            <button
              onClick={handleWeekFailed}
              disabled={exporting}
              className="rounded-lg bg-indigo-500 px-4 py-2 text-xs font-medium text-white hover:bg-indigo-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {getButtonText("Failed This Week (JSON)", "json", "failed")}
            </button>
            <button
              onClick={() => setCustomRange(!customRange)}
              className={`rounded-lg border px-4 py-2 text-xs font-medium hover:bg-slate-800 transition-colors ${
                customRange
                  ? "border-indigo-500 bg-indigo-500/20 text-indigo-300"
                  : "border-slate-700 text-slate-200"
              }`}
            >
              Custom Range
            </button>
            {customRange && (
              <div className="space-y-3 rounded-lg border border-slate-700 bg-slate-950/50 p-4">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Start Date *</label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    max={endDate || new Date().toISOString().split("T")[0]}
                    className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">End Date *</label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    min={startDate || undefined}
                    max={new Date().toISOString().split("T")[0]}
                    className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <button
                  onClick={handleCustomExport}
                  disabled={exporting || !startDate || !endDate}
                  className="w-full rounded-lg bg-indigo-500 px-4 py-2 text-xs font-medium text-white hover:bg-indigo-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {getButtonText("Export CSV", "csv", "custom")}
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <h3 className="text-lg font-semibold text-white">Export Options</h3>
          <p className="mt-2 text-xs text-slate-400">Export all logs or filter by status and date range.</p>
          <div className="mt-4 space-y-3 text-sm text-slate-300">
            <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">All Logs</span>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleExport(null, null, "csv")}
                    disabled={exporting}
                    className="rounded px-3 py-1.5 text-xs bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
                  >
                    {getButtonText("CSV", "csv", "all")}
                  </button>
                  <button
                    onClick={() => handleExport(null, null, "json")}
                    disabled={exporting}
                    className="rounded px-3 py-1.5 text-xs bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
                  >
                    {getButtonText("JSON", "json", "all")}
                  </button>
                </div>
              </div>
              <p className="text-xs text-slate-500">Export all submission logs</p>
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">Success Only</span>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleExport("success", null, "csv")}
                    disabled={exporting}
                    className="rounded px-3 py-1.5 text-xs bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
                  >
                    {getButtonText("CSV", "csv", "success")}
                  </button>
                  <button
                    onClick={() => handleExport("success", null, "json")}
                    disabled={exporting}
                    className="rounded px-3 py-1.5 text-xs bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
                  >
                    {getButtonText("JSON", "json", "success")}
                  </button>
                </div>
              </div>
              <p className="text-xs text-slate-500">Export only successful submissions</p>
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">Failed Only</span>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleExport("failed", null, "csv")}
                    disabled={exporting}
                    className="rounded px-3 py-1.5 text-xs bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
                  >
                    {getButtonText("CSV", "csv", "failed")}
                  </button>
                  <button
                    onClick={() => handleExport("failed", null, "json")}
                    disabled={exporting}
                    className="rounded px-3 py-1.5 text-xs bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
                  >
                    {getButtonText("JSON", "json", "failed")}
                  </button>
                </div>
              </div>
              <p className="text-xs text-slate-500">Export only failed submissions</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
