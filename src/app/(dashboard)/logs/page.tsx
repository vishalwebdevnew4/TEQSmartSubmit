"use client";

import { useEffect, useState, useRef } from "react";
import { LogsSkeleton } from "@/components/skeletons/LogsSkeleton";
import { toast } from "@/lib/toast";

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

  const isPageVisible = useRef(true);
  const lastActivityTime = useRef(Date.now());
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    fetchLogs();
    
    // Page Visibility API - pause polling when tab is hidden
    const handleVisibilityChange = () => {
      isPageVisible.current = !document.hidden;
      if (isPageVisible.current) {
        // Tab became visible, resume polling
        startPolling();
      } else {
        // Tab hidden, stop polling
        stopPolling();
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);

    // Adaptive polling: 2s when active, 10s when idle
    const startPolling = () => {
      stopPolling(); // Clear any existing interval
      
      const getPollInterval = () => {
        const timeSinceActivity = Date.now() - lastActivityTime.current;
        // If user was active in last 30 seconds, use fast polling
        return timeSinceActivity < 30000 ? 2000 : 10000;
      };

      const poll = () => {
        if (isPageVisible.current) {
          fetchLogs(false); // Silent refresh
          intervalRef.current = setTimeout(poll, getPollInterval());
        }
      };

      intervalRef.current = setTimeout(poll, getPollInterval());
    };

    const stopPolling = () => {
      if (intervalRef.current) {
        clearTimeout(intervalRef.current);
        intervalRef.current = null;
      }
    };

    startPolling();
    
    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      stopPolling();
    };
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
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error("Failed to fetch logs:", {
          status: response.status,
          statusText: response.statusText,
          error: errorData
        });
        
        // Show user-friendly error message
        if (response.status === 500) {
          setLogs([]);
          const errorMsg = errorData.detail || errorData.error || "Database connection issue. Please check server logs.";
          toast.error(errorMsg);
        }
        return;
      }
      
        const data = await response.json();
        setLogs(data.logs || []);
        lastActivityTime.current = Date.now(); // Update activity time on successful fetch
      
      // Log for debugging
      if (data.logs && data.logs.length > 0) {
        console.log(`[LogsPage] Loaded ${data.logs.length} logs`);
      } else {
        console.log("[LogsPage] No logs found");
      }
    } catch (error) {
      console.error("Failed to fetch logs:", error);
      setLogs([]);
      toast.error(`Network error: ${error instanceof Error ? error.message : "Failed to connect to server"}`);
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

  const handleClearLogs = async () => {
    // Confirm before clearing
    const confirmed = window.confirm(
      "⚠️ Are you sure you want to delete ALL logs from the database?\n\nThis action cannot be undone."
    );
    
    if (!confirmed) {
      return;
    }

    try {
      const response = await fetch("/api/logs", {
        method: "DELETE",
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        alert(`Failed to clear logs: ${errorData.detail || errorData.error || "Unknown error"}`);
        return;
      }

      const data = await response.json();
      alert(`✅ ${data.message || `Successfully deleted ${data.deletedCount || 0} log(s)`}`);
      
      // Refresh logs after clearing
      fetchLogs(true);
    } catch (error) {
      console.error("Failed to clear logs:", error);
      alert(`Network error: ${error instanceof Error ? error.message : "Failed to connect to server"}`);
    }
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

  const handleCopyLog = async (log: SubmissionLog) => {
    try {
      const logText = `Submission Log #${log.id}\n` +
        `URL: ${log.domain?.url || log.url}\n` +
        `Template: ${log.template?.name || 'N/A'}\n` +
        `Status: ${log.status}\n` +
        `Created: ${new Date(log.createdAt).toLocaleString()}\n` +
        `${log.finishedAt ? `Finished: ${new Date(log.finishedAt).toLocaleString()}\n` : ''}` +
        `${log.finishedAt && log.createdAt ? `Duration: ${Math.round((new Date(log.finishedAt).getTime() - new Date(log.createdAt).getTime()) / 1000)}s\n` : ''}` +
        `\n${'='.repeat(80)}\n` +
        `LOG MESSAGE:\n` +
        `${'='.repeat(80)}\n` +
        `${log.message || 'No log message available'}`;
      
      await navigator.clipboard.writeText(logText);
      
      // Show temporary success message
      const button = document.activeElement as HTMLElement;
      const originalText = button.textContent;
      button.textContent = '✅ Copied!';
      button.classList.add('text-emerald-400');
      setTimeout(() => {
        button.textContent = originalText;
        button.classList.remove('text-emerald-400');
      }, 2000);
    } catch (error) {
      console.error('Failed to copy log:', error);
      alert('Failed to copy log to clipboard');
    }
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

      {logs.length > 0 && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div className="rounded-xl border border-slate-800/50 bg-gradient-to-br from-slate-900/80 to-slate-900/40 backdrop-blur-sm p-5 shadow-lg hover:border-slate-700 transition-colors">
            <p className="text-xs font-semibold text-slate-300 uppercase tracking-wide">Total Logs</p>
            <p className="mt-3 text-2xl font-bold text-white">{logs.length}</p>
          </div>
          <div className="rounded-xl border border-slate-800/50 bg-gradient-to-br from-slate-900/80 to-slate-900/40 backdrop-blur-sm p-5 shadow-lg hover:border-slate-700 transition-colors">
            <p className="text-xs font-semibold text-slate-300 uppercase tracking-wide">Success</p>
            <p className="mt-3 text-2xl font-bold text-emerald-400">
              {logs.filter(l => l.status === "success").length}
            </p>
          </div>
          <div className="rounded-xl border border-slate-800/50 bg-gradient-to-br from-slate-900/80 to-slate-900/40 backdrop-blur-sm p-5 shadow-lg hover:border-slate-700 transition-colors">
            <p className="text-xs font-semibold text-slate-300 uppercase tracking-wide">Failed</p>
            <p className="mt-3 text-2xl font-bold text-rose-400">
              {logs.filter(l => l.status === "failed").length}
            </p>
          </div>
          <div className="rounded-xl border border-slate-800/50 bg-gradient-to-br from-slate-900/80 to-slate-900/40 backdrop-blur-sm p-5 shadow-lg hover:border-slate-700 transition-colors">
            <p className="text-xs font-semibold text-slate-300 uppercase tracking-wide">Running</p>
            <p className="mt-3 text-2xl font-bold text-yellow-400">
              {logs.filter(l => l.status === "running" || l.status === "pending").length}
            </p>
          </div>
        </div>
      )}

      <div className="rounded-xl border border-slate-800/50 bg-gradient-to-br from-slate-900/80 to-slate-900/40 backdrop-blur-sm p-5 shadow-lg">
        <div className="flex flex-wrap gap-3 items-center">
          <button
            onClick={handleRefresh}
            disabled={refreshing || loading}
            className="inline-flex items-center gap-2 rounded-lg border border-slate-700/50 bg-slate-800/50 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-slate-700/50 hover:border-slate-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
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
            className={`inline-flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium transition-all ${
              showFilter 
                ? "border-indigo-500/50 bg-indigo-500/10 text-indigo-300 hover:bg-indigo-500/20" 
                : "border-slate-700/50 bg-slate-800/50 text-slate-200 hover:bg-slate-700/50"
            }`}
          >
            <span>🔍</span>
            Filter {filterStatus && `(${filterStatus})`}
          </button>
          {showFilter && (
            <div className="flex gap-2 items-center">
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="rounded-lg border border-slate-700/50 bg-slate-800/50 px-4 py-2 text-sm text-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all cursor-pointer"
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
            className="inline-flex items-center gap-2 rounded-lg border border-blue-600/50 bg-blue-500/10 px-4 py-2 text-sm font-medium text-blue-400 hover:bg-blue-500/20 transition-all"
          >
            <span>📥</span>
            Export CSV
          </button>
          <button
            onClick={() => handleExport("json")}
            className="inline-flex items-center gap-2 rounded-lg border border-blue-600/50 bg-blue-500/10 px-4 py-2 text-sm font-medium text-blue-400 hover:bg-blue-500/20 transition-all"
          >
            <span>📥</span>
            Export JSON
          </button>
          <button
            onClick={handleClearLogs}
            className="inline-flex items-center gap-2 rounded-lg border border-rose-600/50 bg-rose-500/10 px-4 py-2 text-sm font-medium text-rose-400 hover:bg-rose-500/20 transition-all"
            title="Delete all logs from database"
          >
            <span>🗑️</span>
            Clear Logs
          </button>
        </div>
      </div>

      <div className="space-y-3">
        {logs.length === 0 ? (
          <div className="rounded-xl border border-slate-800/50 bg-gradient-to-br from-slate-900/80 to-slate-900/40 backdrop-blur-sm p-8 text-center shadow-lg">
            <p className="text-sm text-slate-300">No logs found.</p>
          </div>
        ) : (
          logs.map((log) => (
          <div
            key={log.id}
            className="rounded-xl border border-slate-800/50 bg-gradient-to-br from-slate-900/80 to-slate-900/40 backdrop-blur-sm p-5 text-sm shadow-lg hover:border-slate-700 transition-all"
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex-1">
                  <p className="font-medium text-slate-200">{log.domain?.url || log.url}</p>
                  {log.template && (
                    <p className="text-xs text-slate-400 mt-1">Template: {log.template.name}</p>
                  )}
                  <p className="text-xs text-slate-500 mt-1">
                    {new Date(log.createdAt).toLocaleString()}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium border ${getStatusColor(log.status)}`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${
                      log.status === "success" ? "bg-emerald-300" :
                      log.status === "failed" ? "bg-rose-300" :
                      log.status === "pending" || log.status === "running" ? "bg-yellow-300 animate-pulse" :
                      "bg-slate-300"
                    }`}></span>
                    {log.status}
                  </span>
                  {log.message && (
                    <span className="text-xs text-slate-500" title="Logs available">
                      📋
                    </span>
                  )}
                </div>
              </div>
              <div className="mt-3">
                {log.message ? (
                  isLongMessage(log.message) && !expandedLogs.has(log.id) ? (
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
                  )
                ) : (
                  <div className="rounded-lg border border-slate-700 bg-slate-950/60 p-3 text-xs text-slate-400 italic">
                    {log.status === "success" 
                      ? "✅ Submission completed successfully. No detailed logs available." 
                      : log.status === "running" || log.status === "pending"
                      ? "⏳ Automation in progress..."
                      : "No log message available."}
                  </div>
                )}
              </div>
              <div className="mt-3 flex items-center justify-between">
                <div className="flex gap-4 text-xs text-slate-500">
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
                {log.message && (
                  <button
                    onClick={() => handleCopyLog(log)}
                    className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-300 hover:bg-slate-800 hover:border-indigo-500 hover:text-indigo-300 transition-colors flex items-center gap-1.5"
                    title="Copy full log to clipboard"
                  >
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    Copy Log
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
