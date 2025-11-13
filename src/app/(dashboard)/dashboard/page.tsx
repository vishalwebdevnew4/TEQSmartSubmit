const cards = [
  { title: "Domains", value: "48", subtext: "+4 new this week" },
  { title: "Success", value: "312", subtext: "72% completion rate" },
  { title: "Failed", value: "54", subtext: "5 pending retries" },
  { title: "Pending", value: "21", subtext: "Queue scheduled" },
];

const activity = [
  { domain: "acme.com", status: "Success", time: "Just now" },
  { domain: "globex.io", status: "Failed", time: "2m ago" },
  { domain: "initech.org", status: "Success", time: "5m ago" },
  { domain: "umbrella.com", status: "Pending", time: "12m ago" },
];

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <header className="flex flex-col gap-2">
        <h2 className="text-2xl font-semibold text-white">Overview</h2>
        <p className="text-sm text-slate-400">Monitor automation health and recent submission activity.</p>
      </header>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {cards.map((card) => (
          <div key={card.title} className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-sm">
            <p className="text-xs uppercase tracking-wide text-slate-400">{card.title}</p>
            <p className="mt-3 text-2xl font-semibold text-white">{card.value}</p>
            <p className="mt-1 text-xs text-slate-500">{card.subtext}</p>
          </div>
        ))}
      </section>

      <section className="grid gap-4 xl:grid-cols-[2fr_1fr]">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white">Automation Controls</h3>
              <p className="text-xs text-slate-400">Start, pause, or run test submissions.</p>
            </div>
            <div className="flex gap-2">
              <button className="rounded-lg bg-indigo-500 px-4 py-2 text-xs font-medium text-white hover:bg-indigo-400">
                Start Run
              </button>
              <button className="rounded-lg border border-slate-700 px-4 py-2 text-xs font-medium text-slate-200 hover:bg-slate-800">
                Pause
              </button>
              <button className="rounded-lg border border-slate-700 px-4 py-2 text-xs font-medium text-slate-200 hover:bg-slate-800">
                Test Domain
              </button>
            </div>
          </div>
          <div className="mt-6 grid gap-4 rounded-xl border border-dashed border-slate-800 bg-slate-950/60 p-6 text-sm text-slate-400">
            <div className="flex justify-between">
              <span>Current status</span>
              <span className="text-indigo-300">Idle</span>
            </div>
            <div className="flex justify-between">
              <span>Delay</span>
              <span>5 seconds</span>
            </div>
            <div className="flex justify-between">
              <span>Retry limit</span>
              <span>2 attempts</span>
            </div>
            <div className="flex justify-between">
              <span>Last run</span>
              <span>Today, 09:42 AM</span>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <h3 className="text-lg font-semibold text-white">Activity Feed</h3>
          <ul className="mt-4 space-y-3 text-sm">
            {activity.map((item) => (
              <li key={item.domain} className="flex items-center justify-between rounded-lg bg-slate-950/60 px-4 py-3">
                <div>
                  <p className="font-medium text-slate-200">{item.domain}</p>
                  <p className="text-xs text-slate-500">{item.time}</p>
                </div>
                <span className="rounded-full bg-indigo-500/20 px-3 py-1 text-xs text-indigo-300">{item.status}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>
    </div>
  );
}

