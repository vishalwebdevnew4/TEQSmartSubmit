const templates = [
  {
    name: "Default Contact Form",
    fields: ["name", "email", "subject", "message"],
    lastUpdated: "2025-11-12",
  },
  {
    name: "Partner Outreach",
    fields: ["full_name", "work_email", "company", "message"],
    lastUpdated: "2025-11-10",
  },
];

export default function TemplatesPage() {
  return (
    <div className="space-y-6">
      <header>
        <h2 className="text-2xl font-semibold text-white">Form Templates</h2>
        <p className="text-sm text-slate-400">Create reusable mappings that the automation engine relies on.</p>
      </header>

      <button className="rounded-lg bg-indigo-500 px-4 py-2 text-xs font-medium text-white hover:bg-indigo-400">
        New Template
      </button>

      <div className="grid gap-4 md:grid-cols-2">
        {templates.map((template) => (
          <div key={template.name} className="space-y-3 rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white">{template.name}</h3>
                <p className="text-xs text-slate-500">Last updated {template.lastUpdated}</p>
              </div>
              <button className="rounded-lg border border-slate-700 px-3 py-1 text-xs font-medium text-slate-200 hover:bg-slate-800">
                Edit
              </button>
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
              <p className="text-xs text-slate-400">Mapped fields</p>
              <div className="mt-3 flex flex-wrap gap-2 text-xs">
                {template.fields.map((field) => (
                  <span key={field} className="rounded-full bg-indigo-500/20 px-3 py-1 text-indigo-300">
                    {field}
                  </span>
                ))}
              </div>
            </div>
            <div className="text-xs text-slate-400">
              <p>Preview:</p>
              <p className="mt-1 line-clamp-2 text-slate-300">
                name - input[name=&quot;fullname&quot;], email - input#email, message - textarea[name=&quot;message&quot;]
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

