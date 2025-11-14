"use client";

import { useEffect, useState } from "react";

interface SubmissionLog {
  id: number;
  url: string;
  status: string;
  message: string | null;
  createdAt: Date;
  finishedAt: Date | null;
  domain?: {
    id: number;
    url: string;
  };
  template?: {
    id: number;
    name: string;
  };
}

export default function LogsPage() {
  const [logs, setLogs] = useState<SubmissionLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>("");
  const [showFilter, setShowFilter] = useState(false);
  const [expandedLogs, setExpandedLogs] = useState<Set<number>>(new Set());

  useEffect(() => {
    fetchLogs();
  }, [filterStatus]);

  const fetchLogs = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      }
      const params = new URLSearchParams();
      if (filterStatus) params.append("status", filterStatus);
      params.append("limit", "100");

      const response = await fetch(`/api/logs?${params.toString()}`);
      if (response.ok) {
        const data = await response.json();
        setLogs(data.logs || []);
      }
    } catch (error) {
      console.error("Failed to fetch logs:", error);
    } finally {
      setLoading(false);
      if (isRefresh) {
        setRefreshing(false);
      }
    }
  };

  const handleRefresh = () => {
    fetchLogs(true);
  };

  const handleExport = async (format: "csv" | "json") => {
    try {
      const params = new URLSearchParams();
      if (filterStatus) params.append("status", filterStatus);
      params.append("format", format);

      const response = await fetch(`/api/reports/export?${params.toString()}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `submission-logs-${new Date().toISOString().split("T")[0]}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        alert("Failed to export logs");
      }
    } catch (error) {
      console.error("Failed to export logs:", error);
      alert("Failed to export logs");
    }
  };

  const getStatusColor = (status: string) => {
    const normalized = status.toLowerCase();
    if (normalized === "success" || normalized === "completed") {
      return "bg-emerald-500/20 text-emerald-300";
    } else if (normalized === "failed" || normalized === "error") {
      return "bg-rose-500/20 text-rose-300";
    } else if (normalized === "pending" || normalized === "running") {
      return "bg-yellow-500/20 text-yellow-300";
    }
    return "bg-slate-700/50 text-slate-300";
  };

  const toggleLogExpansion = (logId: number) => {
    setExpandedLogs((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(logId)) {
        newSet.delete(logId);
      } else {
        newSet.add(logId);
      }
      return newSet;
    });
  };

  const formatLogMessage = (message: string | null): string[] => {
    if (!message) return [];
    return message.split("\n").filter((line) => line.trim().length > 0);
  };

  const getMessagePreview = (message: string | null, maxLength: number = 150): string => {
    if (!message) return "";
    if (message.length <= maxLength) return message;
    return message.substring(0, maxLength) + "...";
  };

  const isLongMessage = (message: string | null): boolean => {
    return message ? message.length > 150 : false;
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <header className="flex flex-col gap-2">
          <h2 className="text-2xl font-semibold text-white">Submission Logs</h2>
          <p className="text-sm text-slate-400">
            Investigate automation runs, filter by outcome, and export data for reporting.
          </p>
        </header>
        <div className="text-center text-slate-400">Loading logs...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-2">
        <h2 className="text-2xl font-semibold text-white">Submission Logs</h2>
        <p className="text-sm text-slate-400">
          Investigate automation runs, filter by outcome, and export data for reporting.
        </p>
      </header>

      <div className="flex flex-wrap gap-3 text-xs items-center">
        <button
          onClick={handleRefresh}
          disabled={refreshing || loading}
          className="rounded-lg border border-slate-700 px-4 py-2 font-medium text-slate-200 hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          title="Refresh logs"
        >
          <svg
            className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
          {refreshing ? "Refreshing..." : "Refresh"}
        </button>
        <button
          onClick={() => setShowFilter(!showFilter)}
          className={`rounded-lg border px-4 py-2 font-medium hover:bg-slate-800 transition-colors ${
            showFilter ? "border-indigo-500 bg-indigo-500/20 text-indigo-300" : "border-slate-700 text-slate-200"
          }`}
        >
          Filter {filterStatus && `(${filterStatus})`}
        </button>
        {showFilter && (
          <div className="flex gap-2 items-center">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-slate-200"
            >
              <option value="">All Statuses</option>
              <option value="success">Success</option>
              <option value="failed">Failed</option>
              <option value="pending">Pending</option>
              <option value="running">Running</option>
            </select>
          </div>
        )}
        <button
          onClick={() => handleExport("csv")}
          className="rounded-lg border border-slate-700 px-4 py-2 font-medium text-slate-200 hover:bg-slate-800"
        >
          Export CSV
        </button>
        <button
          onClick={() => handleExport("json")}
          className="rounded-lg border border-slate-700 px-4 py-2 font-medium text-slate-200 hover:bg-slate-800"
        >
          Export JSON
        </button>
      </div>

      <div className="space-y-3">
        {logs.length === 0 ? (
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-8 text-center text-sm text-slate-400">
            No logs found.
          </div>
        ) : (
          logs.map((log) => (
          <div
            key={log.id}
            className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 text-sm shadow-sm hover:border-slate-700"
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                  <p className="font-medium text-slate-200">{log.domain?.url || log.url}</p>
                  {log.template && (
                    <p className="text-xs text-slate-400 mt-1">Template: {log.template.name}</p>
                  )}
                  <p className="text-xs text-slate-500 mt-1">
                    {new Date(log.createdAt).toLocaleString()}
                  </p>
                </div>
                <span className={`rounded-full px-3 py-1 text-xs font-semibold ${getStatusColor(log.status)}`}>
                  {log.status}
                </span>
              </div>
              {log.message && (
                <div className="mt-3">
                  {isLongMessage(log.message) && !expandedLogs.has(log.id) ? (
                    <>
                      <div className="rounded-lg border border-slate-700 bg-slate-950/60 p-3 font-mono text-xs text-slate-300 whitespace-pre-wrap break-words">
                        {getMessagePreview(log.message)}
                      </div>
                      <button
                        onClick={() => toggleLogExpansion(log.id)}
                        className="mt-2 text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
                      >
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                        Show full log
                      </button>
                    </>
                  ) : isLongMessage(log.message) && expandedLogs.has(log.id) ? (
                    <>
                      <div className="rounded-lg border border-slate-700 bg-slate-950/60 p-4 font-mono text-xs text-slate-300 whitespace-pre-wrap break-words max-h-[600px] overflow-y-auto">
                        {formatLogMessage(log.message).map((line, idx) => {
                          // Color code different log levels
                          let lineClass = "text-slate-300";
                          if (line.includes("✅") || line.includes("success")) {
                            lineClass = "text-emerald-400";
                          } else if (line.includes("❌") || line.includes("failed") || line.includes("error")) {
                            lineClass = "text-rose-400";
                          } else if (line.includes("⏳") || line.includes("waiting")) {
                            lineClass = "text-yellow-400";
                          } else if (line.includes("🚀") || line.includes("Starting")) {
                            lineClass = "text-blue-400";
                          } else if (line.includes("🔐") || line.includes("CAPTCHA")) {
                            lineClass = "text-purple-400";
                          }
                          return (
                            <div key={idx} className={lineClass}>
                              {line}
                            </div>
                          );
                        })}
                      </div>
                      <button
                        onClick={() => toggleLogExpansion(log.id)}
                        className="mt-2 text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
                      >
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                        </svg>
                        Hide full log
                      </button>
                    </>
                  ) : (
                    <div className="rounded-lg border border-slate-700 bg-slate-950/60 p-3 font-mono text-xs text-slate-300 whitespace-pre-wrap break-words">
                      {formatLogMessage(log.message).map((line, idx) => {
                        let lineClass = "text-slate-300";
                        if (line.includes("✅") || line.includes("success")) {
                          lineClass = "text-emerald-400";
                        } else if (line.includes("❌") || line.includes("failed") || line.includes("error")) {
                          lineClass = "text-rose-400";
                        } else if (line.includes("⏳") || line.includes("waiting")) {
                          lineClass = "text-yellow-400";
                        } else if (line.includes("🚀") || line.includes("Starting")) {
                          lineClass = "text-blue-400";
                        } else if (line.includes("🔐") || line.includes("CAPTCHA")) {
                          lineClass = "text-purple-400";
                        }
                        return (
                          <div key={idx} className={lineClass}>
                            {line}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}
              <div className="mt-3 flex gap-4 text-xs text-slate-500">
                <span>Log ID: {log.id}</span>
                {log.finishedAt && (
                  <span>
                    Finished: {new Date(log.finishedAt).toLocaleString()}
                  </span>
                )}
                {log.finishedAt && log.createdAt && (
                  <span>
                    Duration: {Math.round((new Date(log.finishedAt).getTime() - new Date(log.createdAt).getTime()) / 1000)}s
              </span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
