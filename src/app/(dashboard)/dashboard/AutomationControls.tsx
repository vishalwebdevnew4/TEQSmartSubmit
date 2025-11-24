"use client";

import { useState, useEffect } from "react";

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
  allDomains?: DomainWithTemplate[];
};

type RunStatus = "idle" | "running" | "success" | "error";

export function AutomationControls({ domain, allDomains = [] }: AutomationControlsProps) {
  const [status, setStatus] = useState<RunStatus>("idle");
  const [message, setMessage] = useState<string | null>(null);
  const [lastRun, setLastRun] = useState<Date | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [abortController, setAbortController] = useState<AbortController | null>(null);
  const [runAllDomains, setRunAllDomains] = useState(false);

  const delaySeconds = 5;
  const retryLimit = 2;

  // Check for running submissions on mount and periodically
  useEffect(() => {
    const checkRunningSubmissions = async () => {
      try {
        const response = await fetch("/api/logs?status=running&limit=10");
        if (response.ok) {
          const data = await response.json();
          const runningLogs = data.logs || [];
          
          if (runningLogs.length > 0) {
            // Find running submissions for our domains
            const relevantDomains = runAllDomains && allDomains.length > 0 
              ? allDomains.map(d => d.url)
              : (domain ? [domain.url] : []);
            
            const relevantRunningLogs = runningLogs.filter((log: any) => {
              const logUrl = log.domain?.url || log.url || "";
              return relevantDomains.some(domainUrl => 
                logUrl.includes(domainUrl) || 
                domainUrl.includes(logUrl) ||
                logUrl === domainUrl
              );
            });
            
            if (relevantRunningLogs.length > 0) {
              // Find the most recent running submission
              const latestRunning = relevantRunningLogs[0];
              
              // Restore or update running state
              if (!isRunning) {
                setStatus("running");
                setIsRunning(true);
              }
              
              // Extract and update message from log
              const logMessage = latestRunning.message || "";
              if (logMessage) {
                // Try to find the "Running automation for..." line
                const lines = logMessage.split("\n");
                const runningLine = lines.find((line: string) => 
                  line.includes("Running automation for") || 
                  line.includes("Running") ||
                  line.trim().startsWith("🚀")
                );
                
                if (runningLine) {
                  setMessage(runningLine.trim());
                } else {
                  // Extract domain from log
                  const domainUrl = latestRunning.domain?.url || latestRunning.url || "domain";
                  setMessage(`Running automation for ${domainUrl}...`);
                }
              } else {
                // Fallback message
                const domainUrl = latestRunning.domain?.url || latestRunning.url || "domain";
                setMessage(`Running automation for ${domainUrl}...`);
              }
              
              // Set last run time
              if (latestRunning.createdAt) {
                setLastRun(new Date(latestRunning.createdAt));
              }
            } else if (isRunning && status === "running") {
              // We think we're running but no running logs found for our domains
              // Check if there are recent completed submissions
              const completedResponse = await fetch("/api/logs?limit=5");
              if (completedResponse.ok) {
                const completedData = await completedResponse.json();
                const recentLogs = completedData.logs || [];
                
                if (recentLogs.length > 0) {
                  const latest = recentLogs[0];
                  if (latest.status === "success" || latest.status === "failed") {
                    // Automation completed
                    setStatus(latest.status === "success" ? "success" : "error");
                    setIsRunning(false);
                    if (latest.finishedAt) {
                      setLastRun(new Date(latest.finishedAt));
                    }
                    if (latest.message) {
                      setMessage(latest.message);
                    }
                  }
                }
              }
            }
          } else if (isRunning && status === "running") {
            // No running submissions found, but we think we're running
            // Check if there are recent completed submissions
            const completedResponse = await fetch("/api/logs?limit=5");
            if (completedResponse.ok) {
              const completedData = await completedResponse.json();
              const recentLogs = completedData.logs || [];
              
              if (recentLogs.length > 0) {
                const latest = recentLogs[0];
                if (latest.status === "success" || latest.status === "failed") {
                  // Automation completed
                  setStatus(latest.status === "success" ? "success" : "error");
                  setIsRunning(false);
                  if (latest.finishedAt) {
                    setLastRun(new Date(latest.finishedAt));
                  }
                }
              }
            }
          }
        }
      } catch (error) {
        console.error("Failed to check running submissions:", error);
      }
    };

    // Check immediately on mount
    checkRunningSubmissions();

    // Poll every 3 seconds for running submissions (only if not manually running)
    const intervalId = setInterval(() => {
      // Always check to update status from database
      checkRunningSubmissions();
    }, 3000);

    return () => clearInterval(intervalId);
  }, [domain, allDomains, status, isRunning, runAllDomains]);

  const primaryTemplate = domain?.templates?.[0];
  // When runAllDomains is true, use all domains (they'll be filtered during execution)
  // When false, only use the primary domain (which has templates)
  const domainsToRun = runAllDomains && allDomains.length > 0 ? allDomains : (domain ? [domain] : []);
  
  // Debug logging
  if (runAllDomains) {
    const domainsWithTemplates = allDomains.filter(d => d.templates.length > 0);
    console.log(`[AutomationControls] Run all domains enabled. Total domains: ${allDomains.length}, Domains with templates: ${domainsWithTemplates.length}`);
  }

  // Can run if:
  // - Not currently running
  // - Has at least one domain to run
  // - If runAllDomains is false, the primary domain must have templates
  // - If runAllDomains is true, at least one domain must have templates
  const hasRunnableDomains = runAllDomains 
    ? allDomains.some(d => d.templates.length > 0 && d.isActive)
    : (domain && domain.templates.length > 0 && domain.isActive);
  const canRun = Boolean(domainsToRun.length > 0 && hasRunnableDomains && !isRunning);

  const handleStartRun = async (isTest = false) => {
    if (domainsToRun.length === 0 || isRunning) {
      return;
    }

    setStatus("running");
    setMessage(null);
    setIsRunning(true);
    setIsPaused(false);

    const controller = new AbortController();
    setAbortController(controller);
    
    // Track if this was paused
    let wasPaused = false;
    
    // Set timeout to 6 minutes per domain (slightly longer than API timeout of 5 minutes)
    const timeoutPerDomain = 6 * 60 * 1000;
    const totalTimeout = timeoutPerDomain * domainsToRun.length;
    const timeoutId = setTimeout(() => controller.abort(), totalTimeout);

    try {
      const results: Array<{ domain: string; success: boolean; message: string }> = [];
      
      // Run automation for each domain sequentially
      console.log(`[AutomationControls] Starting run for ${domainsToRun.length} domain(s):`, domainsToRun.map(d => d.url));
      
      // Filter to only domains with templates for progress tracking
      const domainsWithTemplates = domainsToRun.filter(d => d.templates.length > 0);
      let processedCount = 0;
      
      for (let i = 0; i < domainsToRun.length; i++) {
        const currentDomain = domainsToRun[i];
        const currentTemplate = currentDomain.templates[0];
        
        if (!currentTemplate) {
          console.warn(`[AutomationControls] Domain ${currentDomain.url} has no template, skipping`);
          results.push({
            domain: currentDomain.url,
            success: false,
            message: "No template found for this domain. Please add a template in Domain Manager."
          });
          continue;
        }

        // Increment counter only for domains with templates
        processedCount++;
        setMessage(`Running automation for ${currentDomain.url} (${processedCount}/${domainsWithTemplates.length})...`);

        try {
          // Enhance template for test mode
          // Use ONLY local solver (disable hybrid mode by default)
          const templateData = {
            ...currentTemplate.fieldMappings,
            // Headless mode will be determined by the API route based on environment
            // (checks for DISPLAY availability - works on local dev, uses headless on remote servers)
            // For test mode, always show browser
            headless: isTest ? false : undefined, // Let API route decide based on environment
            use_local_captcha_solver: currentTemplate.fieldMappings.use_local_captcha_solver ?? true,
            use_hybrid_captcha_solver: currentTemplate.fieldMappings.use_hybrid_captcha_solver ?? false, // Default to false - local only
            captcha_service: currentTemplate.fieldMappings.captcha_service ?? "local", // Default to local only
          };

          const response = await fetch("/api/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              url: currentDomain.url,
              template: templateData,
              domainId: currentDomain.id,
              templateId: currentTemplate.id,
              isTest: isTest, // Pass test flag
            }),
            signal: controller.signal,
          });

          const payload = await response.json().catch(() => ({}));

          if (!response.ok) {
            results.push({
              domain: currentDomain.url,
              success: false,
              message: payload?.message ?? "Automation run failed."
            });
          } else {
            // Wait for this automation to complete before starting the next one
            const submissionId = payload.submissionId;
            if (submissionId) {
              setMessage(`Waiting for ${currentDomain.url} to complete (${processedCount}/${domainsWithTemplates.length})...`);
              
              // Poll for completion (check every 2 seconds, max 10 minutes per domain)
              let completed = false;
              const maxWaitTime = 10 * 60 * 1000; // 10 minutes
              const startTime = Date.now();
              const pollInterval = 2000; // 2 seconds
              
              while (!completed && (Date.now() - startTime) < maxWaitTime) {
                try {
                  const logResponse = await fetch(`/api/logs?limit=100`);
                  if (logResponse.ok) {
                    const logData = await logResponse.json();
                    const submission = logData.logs?.find((log: any) => log.id === submissionId);
                    
                    if (submission) {
                      if (submission.status === "success" || submission.status === "failed" || submission.status === "completed") {
                        completed = true;
                        results.push({
                          domain: currentDomain.url,
                          success: submission.status === "success",
                          message: submission.message || `Run ${submission.status}`
                        });
                        break;
                      }
                      // Still running, update message
                      if (submission.message) {
                        const lines = submission.message.split("\n");
                        const lastLine = lines[lines.length - 1] || lines[0] || "";
                        if (lastLine.trim()) {
                          setMessage(`${currentDomain.url} (${processedCount}/${domainsWithTemplates.length}): ${lastLine.substring(0, 80)}...`);
                        }
                      }
                    }
                  }
                  
                  // Wait before next poll
                  await new Promise(resolve => setTimeout(resolve, pollInterval));
                } catch (pollError) {
                  console.error("Error polling for completion:", pollError);
                  // Continue polling
                  await new Promise(resolve => setTimeout(resolve, pollInterval));
                }
              }
              
              if (!completed) {
                results.push({
                  domain: currentDomain.url,
                  success: false,
                  message: "Automation timed out (waited 10 minutes)"
                });
              }
            } else {
              results.push({
                domain: currentDomain.url,
                success: true,
                message: payload?.message ?? "Run started successfully."
              });
            }
          }

          // Add delay between domains to avoid rate limiting (only if not the last domain)
          if (i < domainsToRun.length - 1) {
            setMessage(`Waiting ${delaySeconds} seconds before next domain...`);
            await new Promise(resolve => setTimeout(resolve, delaySeconds * 1000));
          }
        } catch (error) {
          if (error instanceof Error && error.name === "AbortError") {
            throw error; // Re-throw abort to break the loop
          }
          results.push({
            domain: currentDomain.url,
            success: false,
            message: error instanceof Error ? error.message : "Unknown error"
          });
        }
      }

      clearTimeout(timeoutId);

      // Summarize results
      const successCount = results.filter(r => r.success).length;
      const failureCount = results.filter(r => !r.success).length;
      
      if (failureCount === 0) {
        setStatus("success");
        setMessage(
          isTest 
            ? `Test completed successfully for all ${domainsToRun.length} domain(s). Check the browser window to verify submissions.`
            : `All ${domainsToRun.length} domain(s) completed successfully.`
        );
      } else if (successCount === 0) {
        setStatus("error");
        setMessage(`All ${domainsToRun.length} domain(s) failed. Check logs for details.`);
      } else {
        setStatus("success");
        setMessage(`${successCount} succeeded, ${failureCount} failed out of ${domainsToRun.length} domain(s).`);
      }
      
      setLastRun(new Date());
      setIsRunning(false);
      setAbortController(null);
    } catch (error) {
      clearTimeout(timeoutId);
      // Check if paused by checking isPaused state
      setIsPaused((prev) => {
        wasPaused = prev;
        return prev;
      });
      
      if (error instanceof Error && error.name === "AbortError" && wasPaused) {
        setStatus("idle");
        setMessage("Automation run paused.");
      } else {
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
      }
      setIsRunning(false);
      setAbortController(null);
    }
  };

  const handlePause = () => {
    if (abortController && isRunning) {
      abortController.abort();
      setIsPaused(true);
      setStatus("idle");
      setMessage("Automation run paused.");
      setIsRunning(false);
      setAbortController(null);
    }
  };

  const handleTestDomain = () => {
    handleStartRun(true); // Pass true to indicate test mode
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
            {domainsToRun.length > 0
              ? runAllDomains && allDomains.length > 1
                ? `Running on ${allDomains.length} domain(s)`
                : `Primary domain: ${domain?.url}${primaryTemplate ? ` • Template: ${primaryTemplate.name}` : ""}`
              : "No domains with templates available."}
          </p>
          {allDomains.length > 1 && (
            <div className="mt-2 space-y-1">
              <label className="flex items-center gap-2 text-xs text-slate-300">
                <input
                  type="checkbox"
                  checked={runAllDomains}
                  onChange={(e) => {
                    setRunAllDomains(e.target.checked);
                    if (e.target.checked) {
                      const domainsWithTemplates = allDomains.filter(d => d.templates.length > 0);
                      const domainsWithoutTemplates = allDomains.filter(d => d.templates.length === 0);
                      let msg = `Will run on ${domainsWithTemplates.length} domain(s) with templates`;
                      if (domainsWithoutTemplates.length > 0) {
                        msg += ` (${domainsWithoutTemplates.length} domain(s) without templates will be skipped)`;
                      }
                      setMessage(msg);
                    } else {
                      setMessage(null);
                    }
                  }}
                  disabled={isRunning}
                  className="rounded border-slate-600 bg-slate-800 text-indigo-500"
                />
                <span>Run on all {allDomains.length} active domains</span>
              </label>
              {runAllDomains && (
                <div className="ml-6 text-xs text-slate-400">
                  <div>• {allDomains.filter(d => d.templates.length > 0).length} with templates: {allDomains.filter(d => d.templates.length > 0).map(d => d.url.split('/')[2] || d.url).join(', ')}</div>
                  {allDomains.filter(d => d.templates.length === 0).length > 0 && (
                    <div className="text-amber-400">• {allDomains.filter(d => d.templates.length === 0).length} without templates (will be skipped): {allDomains.filter(d => d.templates.length === 0).map(d => d.url.split('/')[2] || d.url).join(', ')}</div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => handleStartRun(false)}
            disabled={!canRun}
            className="rounded-lg bg-indigo-500 px-4 py-2 text-xs font-medium text-white hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {status === "running" || isRunning ? "Running…" : "Start Run"}
          </button>
          <button
            type="button"
            onClick={handlePause}
            disabled={!isRunning}
            className="rounded-lg border border-slate-700 px-4 py-2 text-xs font-medium text-slate-200 hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isPaused ? "Paused" : "Pause"}
          </button>
          <button
            type="button"
            disabled={!canRun}
            onClick={handleTestDomain}
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


