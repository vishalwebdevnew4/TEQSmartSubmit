"use client";

import { useState } from "react";

type TemplateFieldMappings = Record<string, unknown>;

type DomainWithTemplate = {
  id: number;
  url: string;
  isActive: boolean;
  category: string | null;
  templates: Array<{
    id: number;
    name: string;
    fieldMappings: TemplateFieldMappings;
  }>;
};

type AutomationControlsProps = {
  domain: DomainWithTemplate | null;
};

type RunStatus = "idle" | "running" | "success" | "error";

export function AutomationControls({ domain }: AutomationControlsProps) {
  const [status, setStatus] = useState<RunStatus>("idle");
  const [message, setMessage] = useState<string | null>(null);
  const [lastRun, setLastRun] = useState<Date | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  const delaySeconds = 5;
  const retryLimit = 2;

  const primaryTemplate = domain?.templates?.[0];

  const canRun = Boolean(domain && primaryTemplate && domain.isActive && !isRunning);

  const handleStartRun = () => {
    if (!domain || !primaryTemplate || isRunning) {
      return;
    }

    setStatus("running");
    setMessage(null);
    setIsRunning(true);

    (async () => {
      const controller = new AbortController();
      // Set timeout to 6 minutes (slightly longer than API timeout of 5 minutes)
      const timeoutId = setTimeout(() => controller.abort(), 6 * 60 * 1000);

      try {
        const response = await fetch("/api/run", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            url: domain.url,
            template: primaryTemplate.fieldMappings,
            domainId: domain.id,
            templateId: primaryTemplate.id,
          }),
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        const payload = await response.json().catch(() => ({}));

        if (!response.ok) {
          setStatus("error");
          setMessage(payload?.message ?? "Automation run failed.");
          setIsRunning(false);
          return;
        }

        setStatus("success");
        setMessage(payload?.message ?? "Run completed successfully.");
        setLastRun(new Date());
        setIsRunning(false);
      } catch (error) {
        clearTimeout(timeoutId);
        setStatus("error");
        if (error instanceof Error) {
          if (error.name === "AbortError") {
            setMessage("Request timed out. The automation may still be running in the background. Check the logs for status.");
          } else {
            setMessage(error.message);
          }
        } else {
          setMessage("Unable to start automation run.");
        }
        setIsRunning(false);
      }
    })();
  };

  const currentStatusLabel =
    status === "running"
      ? "Running"
      : status === "success"
        ? "Completed"
        : status === "error"
          ? "Failed"
          : "Idle";

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white">Automation Controls</h3>
          <p className="text-xs text-slate-400">
            {domain
              ? `Primary domain: ${domain.url}${primaryTemplate ? ` • Template: ${primaryTemplate.name}` : ""}`
              : "No domains with templates available."}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={handleStartRun}
            disabled={!canRun}
            className="rounded-lg bg-indigo-500 px-4 py-2 text-xs font-medium text-white hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {status === "running" || isRunning ? "Running…" : "Start Run"}
          </button>
          <button
            type="button"
            disabled
            className="rounded-lg border border-slate-700 px-4 py-2 text-xs font-medium text-slate-200 opacity-60"
          >
            Pause
          </button>
          <button
            type="button"
            disabled={!canRun}
            onClick={handleStartRun}
            className="rounded-lg border border-slate-700 px-4 py-2 text-xs font-medium text-slate-200 hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Test Domain
          </button>
        </div>
      </div>

      <div className="mt-6 grid gap-4 rounded-xl border border-dashed border-slate-800 bg-slate-950/60 p-6 text-sm text-slate-400">
        <div className="flex justify-between">
          <span>Current status</span>
          <span className="text-indigo-300">{currentStatusLabel}</span>
        </div>
        <div className="flex justify-between">
          <span>Delay</span>
          <span>{delaySeconds} seconds</span>
        </div>
        <div className="flex justify-between">
          <span>Retry limit</span>
          <span>{retryLimit} attempts</span>
        </div>
        <div className="flex justify-between">
          <span>Last run</span>
          <span>{lastRun ? lastRun.toLocaleString() : "Not yet run"}</span>
        </div>
        {message && (
          <div
            className={`rounded-lg border px-3 py-2 text-xs ${
              status === "error"
                ? "border-rose-500/40 bg-rose-500/10 text-rose-200"
                : "border-emerald-500/40 bg-emerald-500/10 text-emerald-200"
            }`}
          >
            {message}
          </div>
        )}
        {!domain && (
          <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-xs text-amber-200">
            Add a domain with at least one template to enable automation controls.
          </div>
        )}
      </div>
    </div>
  );
}


