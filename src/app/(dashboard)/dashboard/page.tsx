import { prisma } from "@/lib/prisma";
import { AutomationControls } from "./AutomationControls";
import { headers } from "next/headers";
import { cache, cacheKeys, cached } from "@/lib/cache";
import { DashboardSkeleton } from "@/components/skeletons/DashboardSkeleton";
import { Suspense } from "react";

// Force dynamic rendering to prevent database connection issues during build
export const dynamic = 'force-dynamic';
export const dynamicParams = true;
export const revalidate = 0;
export const runtime = 'nodejs';

export default async function DashboardPage() {
  // Use headers() to force dynamic rendering - this prevents static generation
  // This is the most reliable way to force dynamic rendering in Next.js 15
  const headersList = await headers();
  
  // Wrap database queries in try-catch to handle connection errors gracefully
  let stats = 0;
  let activeDomains = 0;
  let domainsWithForms = 0;
  let recentActivity: any[] = [];
  let domains: any[] = [];
  let universalTemplates: any[] = [];
  let totalSubmissions = 0;
  let successSubmissions = 0;
  let failedSubmissions = 0;
  
  try {
    [
      stats,
      activeDomains,
      recentActivity,
      domains,
      universalTemplates,
      totalSubmissions,
      successSubmissions,
      failedSubmissions,
    ] = await Promise.all([
      cached(cacheKeys.dashboardStats(), () => prisma.domain.count().catch(() => 0), 30),
      cached(cacheKeys.dashboardStats() + ":active", () => prisma.domain.count({ where: { isActive: true } }).catch(() => 0), 30),
      cached(cacheKeys.dashboardStats() + ":activity", () => prisma.submissionLog.findMany({
        orderBy: { createdAt: "desc" },
        take: 10,
        include: {
          domain: true,
        },
      }).catch(() => []), 10),
      cached(cacheKeys.dashboardDomains(), () => prisma.domain.findMany({
        where: { 
          isActive: true,
        },
        orderBy: { createdAt: "desc" },
        include: {
          templates: {
            orderBy: { createdAt: "asc" },
            take: 10,
          },
        },
      }).catch(() => []), 30),
      cached(cacheKeys.dashboardTemplates(), () => prisma.template.findMany({
        where: { domainId: null },
        orderBy: { createdAt: "desc" },
      }).catch(() => []), 60),
      cached(cacheKeys.dashboardStats() + ":total", () => prisma.submissionLog.count().catch(() => 0), 30),
      cached(cacheKeys.dashboardStats() + ":success", () => prisma.submissionLog.count({ where: { status: "success" } }).catch(() => 0), 30),
      cached(cacheKeys.dashboardStats() + ":failed", () => prisma.submissionLog.count({ where: { status: "failed" } }).catch(() => 0), 30),
    ]);
    
    // Count domains with forms found from the fetched domains
    domainsWithForms = domains.filter((d: any) => d.contactCheckStatus === "found").length;
  } catch (error) {
    // If database connection fails during build, return empty page
    console.error("Database connection error:", error);
    return (
      <div className="space-y-8">
        <header className="flex flex-col gap-2">
          <h2 className="text-2xl font-semibold text-white">Overview</h2>
          <p className="text-sm text-slate-400">Loading dashboard...</p>
        </header>
        <div className="text-center text-slate-400">Dashboard will load at runtime.</div>
      </div>
    );
  }

  // Add universal templates to domains that don't have templates
  const domainsWithTemplates = domains.map((domain) => {
    if (domain.templates.length === 0 && universalTemplates.length > 0) {
      // Add universal templates to domains without templates
      return {
        ...domain,
        templates: universalTemplates.map((t) => ({
          id: t.id,
          name: t.name,
          description: t.description,
          fieldMappings: t.fieldMappings,
          createdAt: t.createdAt,
          updatedAt: t.updatedAt,
          domainId: null,
          domain: null, // Universal templates don't belong to a domain
        })),
      };
    }
    return domain;
  });

  // Filter to only domains with forms found and templates
  const activeDomainsWithTemplates = domainsWithTemplates.filter(
    (domain) => domain.templates.length > 0 && domain.contactCheckStatus === "found"
  );
  const primaryDomain = activeDomainsWithTemplates[0] ?? null;
  
  // Debug: Log template counts
  console.log(`[Dashboard] Total domains: ${domains.length}, Universal templates: ${universalTemplates.length}, Domains with templates: ${activeDomainsWithTemplates.length}`);
  
  // Pass ALL domains (with universal templates added where needed) so user can run on all
  // Domains without templates will be skipped with a clear message

  return (
    <Suspense fallback={<DashboardSkeleton />}>
      <div className="space-y-8">
        <header className="flex flex-col gap-2">
          <h2 className="text-2xl font-semibold text-white">Overview</h2>
          <p className="text-sm text-slate-400">Monitor automation health and recent submission activity.</p>
        </header>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-sm hover:border-slate-700 transition-colors">
          <p className="text-xs uppercase tracking-wide text-slate-400">Total Domains</p>
          <p className="mt-3 text-2xl font-semibold text-white">{stats}</p>
          <p className="mt-1 text-xs text-slate-500">{activeDomains} active</p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-sm hover:border-slate-700 transition-colors">
          <p className="text-xs uppercase tracking-wide text-slate-400">Forms Found</p>
          <p className="mt-3 text-2xl font-semibold text-emerald-400">{domainsWithForms}</p>
          <p className="mt-1 text-xs text-slate-500">Ready for automation</p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-sm hover:border-slate-700 transition-colors">
          <p className="text-xs uppercase tracking-wide text-slate-400">Success Rate</p>
          <p className="mt-3 text-2xl font-semibold text-white">
            {totalSubmissions > 0 
              ? Math.round((successSubmissions / totalSubmissions) * 100) 
              : 0}%
          </p>
          <p className="mt-1 text-xs text-slate-500">
            {successSubmissions} of {totalSubmissions} succeeded
          </p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-sm hover:border-slate-700 transition-colors">
          <p className="text-xs uppercase tracking-wide text-slate-400">Ready Domains</p>
          <p className="mt-3 text-2xl font-semibold text-indigo-400">{activeDomainsWithTemplates.length}</p>
          <p className="mt-1 text-xs text-slate-500">With templates & forms</p>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-sm hover:border-slate-700 transition-colors">
          <p className="text-xs uppercase tracking-wide text-slate-400">Total Submissions</p>
          <p className="mt-3 text-2xl font-semibold text-white">{totalSubmissions}</p>
          <p className="mt-1 text-xs text-slate-500">All time submissions</p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-sm hover:border-slate-700 transition-colors">
          <p className="text-xs uppercase tracking-wide text-slate-400">Recent Success</p>
          <p className="mt-3 text-2xl font-semibold text-emerald-400">
            {recentActivity.filter((item) => item.status === "success").length}
          </p>
          <p className="mt-1 text-xs text-slate-500">Last 10 runs</p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-sm hover:border-slate-700 transition-colors">
          <p className="text-xs uppercase tracking-wide text-slate-400">Recent Failures</p>
          <p className="mt-3 text-2xl font-semibold text-rose-400">
            {recentActivity.filter((item) => item.status !== "success").length}
          </p>
          <p className="mt-1 text-xs text-slate-500">Last 10 runs</p>
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-[2fr_1fr]">
        <AutomationControls 
          domain={primaryDomain as any} 
          allDomains={domainsWithTemplates as any}
        />

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Recent Activity</h3>
            <a 
              href="/logs" 
              className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors"
            >
              View all →
            </a>
          </div>
          <ul className="mt-4 space-y-2 text-sm max-h-[400px] overflow-y-auto">
            {recentActivity.length === 0 ? (
              <li className="rounded-lg bg-slate-950/60 px-4 py-6 text-center text-xs text-slate-500">
                No recent automation runs yet.
              </li>
            ) : (
              recentActivity.map((item) => (
                <li
                  key={item.id}
                  className="flex items-center justify-between rounded-lg bg-slate-950/60 px-4 py-3 hover:bg-slate-900/80 transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-slate-200 truncate">
                      {item.domain?.contactPageUrl || item.domain?.url || "Unknown domain"}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">
                      {item.domain?.contactPageUrl && item.domain?.url && item.domain.contactPageUrl !== item.domain.url && (
                        <span className="text-slate-600">Domain: {item.domain.url} • </span>
                      )}
                      {new Date(item.createdAt).toLocaleString()}
                    </p>
                  </div>
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-medium ml-2 flex-shrink-0 ${
                      item.status === "success"
                        ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                        : item.status === "failed"
                          ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                          : item.status === "running"
                            ? "bg-blue-500/20 text-blue-300 border border-blue-500/30"
                            : "bg-slate-700/50 text-slate-300 border border-slate-600/30"
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
    </Suspense>
  );
}
