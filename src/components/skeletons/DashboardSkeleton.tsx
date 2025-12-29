export function DashboardSkeleton() {
  return (
    <div className="space-y-8 animate-pulse">
      <header className="flex flex-col gap-2">
        <div className="h-8 w-48 bg-slate-800 rounded-lg"></div>
        <div className="h-4 w-96 bg-slate-800 rounded-lg"></div>
      </header>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="rounded-xl border border-slate-800/50 bg-gradient-to-br from-slate-900/80 to-slate-900/40 backdrop-blur-sm p-6 shadow-lg">
            <div className="h-4 w-24 bg-slate-800 rounded mb-3"></div>
            <div className="h-8 w-16 bg-slate-800 rounded mb-2"></div>
            <div className="h-3 w-32 bg-slate-800 rounded"></div>
          </div>
        ))}
      </section>

      <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-800/50 bg-gradient-to-br from-slate-900/80 to-slate-900/40 backdrop-blur-sm p-6 shadow-lg">
          <div className="h-6 w-32 bg-slate-800 rounded mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="h-10 w-10 bg-slate-800 rounded-full"></div>
                <div className="flex-1">
                  <div className="h-4 w-48 bg-slate-800 rounded mb-2"></div>
                  <div className="h-3 w-32 bg-slate-800 rounded"></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-xl border border-slate-800/50 bg-gradient-to-br from-slate-900/80 to-slate-900/40 backdrop-blur-sm p-6 shadow-lg">
          <div className="h-6 w-32 bg-slate-800 rounded mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="h-10 w-10 bg-slate-800 rounded-full"></div>
                <div className="flex-1">
                  <div className="h-4 w-48 bg-slate-800 rounded mb-2"></div>
                  <div className="h-3 w-32 bg-slate-800 rounded"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

