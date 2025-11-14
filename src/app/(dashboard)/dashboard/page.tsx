import { prisma } from "@/lib/prisma";
import { AutomationControls } from "./AutomationControls";

export default async function DashboardPage() {
  const [stats, recentActivity, domains] = await Promise.all([
    prisma.domain.count(),
    prisma.submissionLog.findMany({
      orderBy: { createdAt: "desc" },
      take: 6,
      include: {
        domain: { select: { url: true } },
      },
    }),
    prisma.domain.findMany({
      where: { isActive: true },
      orderBy: { createdAt: "desc" },
      include: {
        templates: {
          orderBy: { createdAt: "asc" },
          take: 3,
        },
      },
    }),
  ]);

  const primaryDomain = domains.find((domain) => domain.templates.length > 0) ?? null;

  return (
    <div className="space-y-8">
      <header className="flex flex-col gap-2">
        <h2 className="text-2xl font-semibold text-white">Overview</h2>
        <p className="text-sm text-slate-400">Monitor automation health and recent submission activity.</p>
      </header>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-sm">
          <p className="text-xs uppercase tracking-wide text-slate-400">Domains</p>
          <p className="mt-3 text-2xl font-semibold text-white">{stats}</p>
          <p className="mt-1 text-xs text-slate-500">Active domains ready for automation</p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-sm">
          <p className="text-xs uppercase tracking-wide text-slate-400">Recent success</p>
          <p className="mt-3 text-2xl font-semibold text-white">
            {recentActivity.filter((item) => item.status === "success").length}
          </p>
          <p className="mt-1 text-xs text-slate-500">Successful submissions (last 6 runs)</p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-sm">
          <p className="text-xs uppercase tracking-wide text-slate-400">Recent failures</p>
          <p className="mt-3 text-2xl font-semibold text-white">
            {recentActivity.filter((item) => item.status !== "success").length}
          </p>
          <p className="mt-1 text-xs text-slate-500">Runs needing attention</p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-sm">
          <p className="text-xs uppercase tracking-wide text-slate-400">Test template</p>
          <p className="mt-3 text-2xl font-semibold text-white">
            {primaryDomain ? primaryDomain.templates[0]?.name ?? "—" : "No template"}
          </p>
          <p className="mt-1 text-xs text-slate-500">
            {primaryDomain?.url ?? "Assign a template to enable automation"}
          </p>
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-[2fr_1fr]">
        <AutomationControls domain={primaryDomain} />

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <h3 className="text-lg font-semibold text-white">Activity Feed</h3>
          <ul className="mt-4 space-y-3 text-sm">
            {recentActivity.length === 0 ? (
              <li className="rounded-lg bg-slate-950/60 px-4 py-6 text-center text-xs text-slate-500">
                No recent automation runs yet.
              </li>
            ) : (
              recentActivity.map((item) => (
                <li
                  key={item.id}
                  className="flex items-center justify-between rounded-lg bg-slate-950/60 px-4 py-3"
                >
                  <div>
                    <p className="font-medium text-slate-200">{item.domain?.url ?? "Unknown domain"}</p>
                    <p className="text-xs text-slate-500">{item.createdAt.toLocaleString()}</p>
                  </div>
                  <span
                    className={`rounded-full px-3 py-1 text-xs ${
                      item.status === "success"
                        ? "bg-emerald-500/20 text-emerald-300"
                        : item.status === "failed"
                          ? "bg-rose-500/20 text-rose-300"
                          : "bg-slate-700/50 text-slate-300"
                    }`}
                  >
                    {item.status}
                  </span>
                </li>
              ))
            )}
          </ul>
        </div>
      </section>
    </div>
  );
}

