const domains = [
  { url: "acme.com/contact", status: "Active", category: "Technology" },
  { url: "globex.io/support", status: "Disabled", category: "Finance" },
  { url: "initech.org/forms", status: "Active", category: "B2B" },
];

export default function DomainsPage() {
  return (
    <div className="space-y-6">
      <header>
        <h2 className="text-2xl font-semibold text-white">Domain Manager</h2>
        <p className="text-sm text-slate-400">Manage the queue of domains for automated submissions.</p>
      </header>

      <div className="flex flex-wrap gap-3">
        <button className="rounded-lg bg-indigo-500 px-4 py-2 text-xs font-medium text-white hover:bg-indigo-400">
          Add Domain
        </button>
        <button className="rounded-lg border border-slate-700 px-4 py-2 text-xs font-medium text-slate-200 hover:bg-slate-800">
          Upload CSV
        </button>
        <button className="rounded-lg border border-slate-700 px-4 py-2 text-xs font-medium text-slate-200 hover:bg-slate-800">
          Bulk Enable
        </button>
      </div>

      <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/60">
        <table className="min-w-full border-collapse text-left text-sm">
          <thead className="bg-slate-900/80 text-xs uppercase tracking-wide text-slate-400">
            <tr>
              <th className="px-6 py-4">Domain URL</th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4">Category</th>
              <th className="px-6 py-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {domains.map((domain) => (
              <tr key={domain.url} className="hover:bg-slate-900/80">
                <td className="px-6 py-4 font-medium text-slate-100">{domain.url}</td>
                <td className="px-6 py-4 text-xs">
                  <span className="rounded-full bg-emerald-500/10 px-3 py-1 font-semibold text-emerald-300">
                    {domain.status}
                  </span>
                </td>
                <td className="px-6 py-4 text-slate-300">{domain.category}</td>
                <td className="px-6 py-4 text-right text-xs text-slate-400">
                  <button className="mr-3 hover:text-indigo-300">Edit</button>
                  <button className="hover:text-rose-300">Remove</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

