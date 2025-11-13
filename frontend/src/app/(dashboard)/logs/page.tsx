const logs = [
  {
    id: "LOG-1024",
    domain: "acme.com",
    status: "Success",
    timestamp: "2025-11-13 09:42",
    message: "Submission accepted",
  },
  {
    id: "LOG-1023",
    domain: "globex.io",
    status: "Failed",
    timestamp: "2025-11-13 09:39",
    message: "Captcha encountered",
  },
  {
    id: "LOG-1022",
    domain: "initech.org",
    status: "Success",
    timestamp: "2025-11-13 09:35",
    message: "Completed in 8.2s",
  },
];

export default function LogsPage() {
  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-2">
        <h2 className="text-2xl font-semibold text-white">Submission Logs</h2>
        <p className="text-sm text-slate-400">
          Investigate automation runs, filter by outcome, and export data for reporting.
        </p>
      </header>

      <div className="flex flex-wrap gap-3 text-xs">
        <button className="rounded-lg border border-slate-700 px-4 py-2 font-medium text-slate-200 hover:bg-slate-800">
          Filter
        </button>
        <button className="rounded-lg border border-slate-700 px-4 py-2 font-medium text-slate-200 hover:bg-slate-800">
          Export CSV
        </button>
        <button className="rounded-lg border border-slate-700 px-4 py-2 font-medium text-slate-200 hover:bg-slate-800">
          Export PDF
        </button>
        <button className="rounded-lg border border-rose-500/50 px-4 py-2 font-medium text-rose-200 hover:bg-rose-500/10">
          Clear Logs
        </button>
      </div>

      <div className="space-y-3">
        {logs.map((log) => (
          <div
            key={log.id}
            className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 text-sm shadow-sm hover:border-slate-700"
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="font-medium text-slate-200">{log.domain}</p>
                <p className="text-xs text-slate-500">{log.timestamp}</p>
              </div>
              <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-300">
                {log.status}
              </span>
            </div>
            <p className="mt-3 text-slate-300">{log.message}</p>
            <p className="mt-2 text-xs text-slate-500">Log ID: {log.id}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

