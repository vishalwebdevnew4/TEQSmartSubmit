"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

export default function LoginPage() {
  const router = useRouter();
  const { login, isAuthenticated, isHydrated } = useAuth();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    
    if (isHydrated && isAuthenticated) {
      router.replace("/dashboard");
    }
  }, [isAuthenticated, isHydrated, router]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    
    const result = await login(form.username.trim(), form.password);
    if (!result.success) {
      setError(result.message);
      return;
    }
    
    router.push("/dashboard");
  }

  if (!mounted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-slate-400">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-950 text-slate-100 px-4">
      <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900/70 p-8 shadow-xl backdrop-blur">
        <div className="mb-8 text-center">
          {/* Google Chrome-style logo colors */}
          <div className="flex items-center justify-center mb-4">
            <div className="relative w-16 h-16">
              {/* Chrome logo colors: Red, Yellow, Green, Blue */}
              <div className="absolute inset-0 rounded-full bg-gradient-to-br from-red-500 via-yellow-500 to-green-500"></div>
              <div className="absolute inset-0 rounded-full bg-gradient-to-tr from-blue-500 via-transparent to-transparent"></div>
              <div className="absolute inset-2 rounded-full bg-slate-900"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-8 h-8 rounded-full bg-slate-900"></div>
              </div>
            </div>
          </div>
          <h1 className="text-2xl font-semibold text-white">TEQSmartSubmit</h1>
          <p className="mt-2 text-sm text-slate-400">Sign in to manage automation runs</p>
        </div>

        <form className="space-y-6" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-slate-300">
              Username
            </label>
            <input
              id="username"
              name="username"
              type="text"
              autoComplete="username"
              value={form.username}
              onChange={(event) => setForm((prev) => ({ ...prev, username: event.target.value }))}
              className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
              placeholder="admin"
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-slate-300">
              Password
            </label>
            <div className="relative mt-2">
              <input
                id="password"
                name="password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                value={form.password}
                onChange={(event) => setForm((prev) => ({ ...prev, password: event.target.value }))}
                className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 pr-10 text-sm text-slate-100 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
                placeholder="••••••••"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword((prev) => !prev)}
                className="absolute inset-y-0 right-2 flex items-center text-xs text-slate-400 hover:text-slate-200"
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>
          </div>

          {error && <p className="text-xs text-red-400">{error}</p>}

          <button
            type="submit"
            className="w-full rounded-lg bg-gradient-to-r from-blue-500 via-green-500 to-yellow-500 px-4 py-2 text-sm font-medium text-white hover:from-blue-600 hover:via-green-600 hover:to-yellow-600 focus:outline-none focus:ring-2 focus:ring-blue-500/60 transition-all"
          >
            Sign in
          </button>
        </form>

        <div className="mt-6 text-xs text-slate-500 text-center">
          <Link href="#" className="pointer-events-none opacity-50">
            Registration restricted • Admin invite required
          </Link>
        </div>
      </div>
      <p className="mt-8 text-xs text-slate-500">Internal access only • TEQTOP Automation</p>
    </div>
  );
}
