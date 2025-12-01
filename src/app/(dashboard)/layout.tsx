"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { PropsWithChildren, useEffect } from "react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";

const navItems = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/businesses", label: "Businesses" },
  { href: "/domains", label: "Domains" },
  { href: "/templates", label: "Templates" },
  { href: "/templates/versions", label: "Versions" },
  { href: "/deployments", label: "Deployments" },
  { href: "/clients", label: "Clients" },
  { href: "/analytics", label: "Analytics" },
  { href: "/logs", label: "Logs" },
  { href: "/reports", label: "Reports" },
  { href: "/settings", label: "Settings" },
];

export default function DashboardLayout({ children }: PropsWithChildren) {
  const pathname = usePathname();
  const router = useRouter();
  const { isAuthenticated, isHydrated, user, logout } = useAuth();

  useEffect(() => {
    if (isHydrated && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, isHydrated, router]);

  function handleLogout() {
    logout();
    router.replace("/login");
  }

  return (
    <div className="grid min-h-screen grid-cols-[260px_1fr] bg-slate-950 text-slate-100">
      <aside className="flex flex-col border-r border-slate-800 bg-slate-900/70 px-6 py-8">
        <div>
          <h1 className="text-lg font-semibold text-white">TEQSmartSubmit</h1>
          <p className="mt-1 text-xs text-slate-400">Automation Control Center</p>
          {user && <p className="mt-3 text-xs text-slate-500">Signed in as {user.username}</p>}
        </div>
        <nav className="mt-10 space-y-2 text-sm">
          {navItems.map((item) => {
            // Improved active state detection
            // Exact match or pathname starts with the href (for nested routes)
            // Special handling for dashboard (only exact match)
            const isActive = item.href === "/dashboard" 
              ? pathname === "/dashboard" || pathname === "/"
              : pathname === item.href || pathname.startsWith(item.href + "/");
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "block rounded-lg px-3 py-2 font-medium transition-colors",
                  isActive 
                    ? "bg-indigo-500/20 text-indigo-300 border-l-2 border-indigo-500" 
                    : "text-slate-300 hover:bg-slate-800/70 hover:text-white"
                )}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="mt-auto space-y-3 text-xs text-slate-500">
          <button
            onClick={handleLogout}
            className="w-full rounded-lg border border-slate-700 px-3 py-2 text-left font-medium text-slate-200 hover:bg-slate-800 text-sm"
          >
            Logout
          </button>
          <p>Next run: Scheduled</p>
          <p>Version: 0.1.0</p>
        </div>
      </aside>
      <main className="flex flex-col gap-6 bg-slate-950 px-10 py-8">{children}</main>
    </div>
  );
}

