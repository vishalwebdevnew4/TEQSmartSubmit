export default function ReportsPage() {
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
          <h3 className="text-lg font-semibold text-white">Quick Filters</h3>
          <p className="mt-2 text-xs text-slate-400">Choose presets to export recent automation data.</p>
          <div className="mt-4 grid gap-3">
            <button className="rounded-lg bg-indigo-500 px-4 py-2 text-xs font-medium text-white hover:bg-indigo-400">
              Success Today (CSV)
            </button>
            <button className="rounded-lg bg-indigo-500 px-4 py-2 text-xs font-medium text-white hover:bg-indigo-400">
              Failed This Week (PDF)
            </button>
            <button className="rounded-lg border border-slate-700 px-4 py-2 text-xs font-medium text-slate-200 hover:bg-slate-800">
              Custom Range
            </button>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <h3 className="text-lg font-semibold text-white">Scheduled Exports</h3>
          <p className="mt-2 text-xs text-slate-400">Set up recurring exports and email delivery.</p>
          <ul className="mt-4 space-y-4 text-sm text-slate-300">
            <li className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
              <div className="flex items-center justify-between">
                <span>Weekly Success Summary</span>
                <span className="text-xs text-slate-500">Fridays • 08:00</span>
              </div>
              <p className="mt-2 text-xs text-slate-500">Format: CSV • Recipients: automation@teqtop.com</p>
            </li>
            <li className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
              <div className="flex items-center justify-between">
                <span>Monthly Failure Digest</span>
                <span className="text-xs text-slate-500">1st of month • 09:00</span>
              </div>
              <p className="mt-2 text-xs text-slate-500">Format: PDF • Recipients: qa@teqtop.com</p>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

