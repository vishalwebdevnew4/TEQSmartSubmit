"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

type FormState = {
  username: string;
  password: string;
  confirmPassword: string;
};

const initialForm: FormState = {
  username: "",
  password: "",
  confirmPassword: "",
};

export default function RegisterPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { registerAdmin, isAuthenticated } = useAuth();

  const inviteToken = useMemo(() => searchParams.get("token") ?? "", [searchParams]);
  const [form, setForm] = useState<FormState>(initialForm);
  const [status, setStatus] = useState<"idle" | "loading" | "success">("idle");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!inviteToken) {
      router.replace("/login");
    }
  }, [inviteToken, router]);

  if (!inviteToken) {
    return null;
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (status === "loading") {
      return;
    }

    if (!form.username.trim() || !form.password) {
      setError("Username and password are required.");
      return;
    }
    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setStatus("loading");
    setError(null);

    const result = await registerAdmin(
      { username: form.username.trim(), password: form.password },
      inviteToken,
    );

    if (!result.success) {
      setStatus("idle");
      setError(result.message);
      return;
    }

    setStatus("success");
    setForm(initialForm);
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 px-4 py-16">
      <div className="mx-auto max-w-lg rounded-2xl border border-slate-800 bg-slate-900/70 p-8 shadow-xl">
        <h1 className="text-2xl font-semibold text-white">Admin Registration</h1>
        <p className="mt-2 text-sm text-slate-400">
          Invite-only portal for creating internal administrator accounts.
        </p>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
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
              className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/40"
              placeholder="admin"
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-slate-300">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="new-password"
              value={form.password}
              onChange={(event) => setForm((prev) => ({ ...prev, password: event.target.value }))}
              className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/40"
              placeholder="Strong password"
              required
            />
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-slate-300">
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              autoComplete="new-password"
              value={form.confirmPassword}
              onChange={(event) => setForm((prev) => ({ ...prev, confirmPassword: event.target.value }))}
              className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/40"
              placeholder="Repeat password"
              required
            />
          </div>

          {error && <p className="text-xs text-rose-400">{error}</p>}
          {status === "success" && (
            <p className="text-xs text-emerald-400">
              Admin user created successfully. Share credentials securely and ask them to sign in.
            </p>
          )}

          <button
            type="submit"
            className="w-full rounded-lg bg-indigo-500 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/60 disabled:cursor-not-allowed disabled:opacity-70"
            disabled={status === "loading"}
          >
            {status === "loading" ? "Creating..." : "Create Admin"}
          </button>
        </form>

        <div className="mt-6 rounded-xl border border-slate-800 bg-slate-950/60 p-4 text-xs text-slate-400">
          <p>
            Invitation token detected: <span className="text-indigo-300">active</span>.{" "}
            {isAuthenticated
              ? "You are signed in; registrations will be attributed to your session."
              : "After creating the first admin, log in at /login to manage submissions."}
          </p>
        </div>
      </div>
    </div>
  );
}

