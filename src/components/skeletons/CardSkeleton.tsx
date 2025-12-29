interface CardSkeletonProps {
  lines?: number;
  showHeader?: boolean;
  showFooter?: boolean;
}

export function CardSkeleton({ lines = 3, showHeader = true, showFooter = false }: CardSkeletonProps) {
  return (
    <div className="rounded-xl border border-slate-800/50 bg-gradient-to-br from-slate-900/80 to-slate-900/40 backdrop-blur-sm p-6 shadow-lg animate-pulse">
      {showHeader && (
        <div className="mb-4">
          <div className="h-6 w-32 bg-slate-800 rounded mb-2"></div>
          <div className="h-4 w-48 bg-slate-800 rounded"></div>
        </div>
      )}
      <div className="space-y-3">
        {Array.from({ length: lines }).map((_, i) => (
          <div key={i} className="h-4 bg-slate-800 rounded" style={{ width: `${100 - i * 10}%` }}></div>
        ))}
      </div>
      {showFooter && (
        <div className="mt-4 pt-4 border-t border-slate-800/50">
          <div className="h-4 w-24 bg-slate-800 rounded"></div>
        </div>
      )}
    </div>
  );
}

