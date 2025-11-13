const settingsGroups = [
  {
    title: "Automation",
    items: [
      { label: "Submission delay (seconds)", value: "5" },
      { label: "Retry attempts", value: "2" },
      { label: "Concurrent sessions", value: "3" },
    ],
  },
  {
    title: "Stealth",
    items: [
      { label: "Proxy rotation", value: "Enabled" },
      { label: "User-agent pool", value: "Desktop • Mobile" },
      { label: "Headless mode", value: "Enabled" },
    ],
  },
  {
    title: "Notifications",
    items: [
      { label: "Slack alerts", value: "Automation Channel" },
      { label: "Email summaries", value: "Daily 09:00" },
      { label: "Failure escalation", value: "After 3 attempts" },
    ],
  },
];

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <header>
        <h2 className="text-2xl font-semibold text-white">System Settings</h2>
        <p className="text-sm text-slate-400">Tune automation parameters, proxies, and alerting preferences.</p>
      </header>

      <div className="grid gap-4 lg:grid-cols-2">
        {settingsGroups.map((group) => (
          <section key={group.title} className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">{group.title}</h3>
              <button className="rounded-lg border border-slate-700 px-3 py-1 text-xs font-medium text-slate-200 hover:bg-slate-800">
                Edit
              </button>
            </div>
            <ul className="mt-4 space-y-3 text-sm text-slate-300">
              {group.items.map((item) => (
                <li key={item.label} className="flex justify-between rounded-xl bg-slate-950/40 px-4 py-3">
                  <span>{item.label}</span>
                  <span className="text-slate-400">{item.value}</span>
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
    </div>
  );
}

