export function LogsSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <header className="flex flex-col gap-2">
        <div className="h-8 w-48 bg-slate-800 rounded-lg"></div>
        <div className="h-4 w-96 bg-slate-800 rounded-lg"></div>
      </header>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="rounded-xl border border-slate-800/50 bg-gradient-to-br from-slate-900/80 to-slate-900/40 backdrop-blur-sm p-5 shadow-lg">
            <div className="h-3 w-20 bg-slate-800 rounded mb-3"></div>
            <div className="h-8 w-16 bg-slate-800 rounded"></div>
          </div>
        ))}
      </div>

      <div className="rounded-xl border border-slate-800/50 bg-gradient-to-br from-slate-900/80 to-slate-900/40 backdrop-blur-sm p-5 shadow-lg">
        <div className="h-6 w-32 bg-slate-800 rounded mb-4"></div>
        <div className="flex flex-wrap gap-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-9 w-24 bg-slate-800 rounded-lg"></div>
          ))}
        </div>
      </div>

      <div className="space-y-3">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((i) => (
          <div key={i} className="rounded-xl border border-slate-800/50 bg-gradient-to-br from-slate-900/80 to-slate-900/40 backdrop-blur-sm p-5 shadow-lg">
            <div className="flex items-center justify-between mb-3">
              <div className="flex-1">
                <div className="h-5 w-64 bg-slate-800 rounded mb-2"></div>
                <div className="h-4 w-48 bg-slate-800 rounded mb-1"></div>
                <div className="h-3 w-32 bg-slate-800 rounded"></div>
              </div>
              <div className="h-6 w-20 bg-slate-800 rounded-full"></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

