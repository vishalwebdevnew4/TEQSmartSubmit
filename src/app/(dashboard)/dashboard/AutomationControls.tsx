"use client";

import { useState, useEffect, useRef } from "react";

type TemplateFieldMappings = Record<string, unknown>;

type DomainWithTemplate = {
  id: number;
  url: string;
  isActive: boolean;
  category: string | null;
  contactCheckStatus: string | null;
  contactPageUrl: string | null;
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

type StartRunOptions = {
  isTest?: boolean;
  restartMode?: boolean;
  resumeStoredState?: boolean;
};

type PersistedAutomationState = {
  status: "idle" | "running" | "paused" | "cancelled" | "completed" | "interrupted";
  isTest: boolean;
  runAllDomains: boolean;
  batchSize: number;
  delaySeconds: number;
  retryLimit: number;
  startedAt: string | null;
  lastUpdatedAt: string;
  totalDomains: number;
  processedDomains: number;
  currentBatch: number;
  totalBatches: number;
  currentDomainId: number | null;
  currentDomainUrl: string | null;
  pendingDomainIds: number[];
  completedDomainIds: number[];
  failedDomainIds: number[];
  skippedDomainIds: number[];
  message: string | null;
};

export function AutomationControls({ domain, allDomains = [] }: AutomationControlsProps) {
  const [status, setStatus] = useState<RunStatus>("idle");
  const [message, setMessage] = useState<string | null>(null);
  const [lastRun, setLastRun] = useState<Date | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [abortController, setAbortController] = useState<AbortController | null>(null);
  const [runAllDomains, setRunAllDomains] = useState(false);
  const [batchSize, setBatchSize] = useState(10);
  const [currentBatch, setCurrentBatch] = useState(0);
  const [totalBatches, setTotalBatches] = useState(0);
  const [startTime, setStartTime] = useState<Date | null>(null);
  const [elapsedTime, setElapsedTime] = useState<string>("");
  const [averageTimePerDomain, setAverageTimePerDomain] = useState(0); // in seconds (static calculation)
  const [recheckingContacts, setRecheckingContacts] = useState(false);
  const [persistedRunState, setPersistedRunState] = useState<PersistedAutomationState | null>(null);

  // Refs for polling - must be at top level, not inside useEffect
  const isPageVisible = useRef(true);
  const lastActivityTime = useRef(Date.now());
  const stopActionRef = useRef<"pause" | "cancel" | null>(null);
  const currentSubmissionIdRef = useRef<number | null>(null);

  const delaySeconds = 5;
  const retryLimit = 2;

  const savePersistedRunState = async (nextState: PersistedAutomationState | null) => {
    setPersistedRunState(nextState);
    try {
      await fetch("/api/settings", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          key: "automation_run_state",
          value: nextState ? JSON.stringify(nextState) : "",
        }),
      });
    } catch (error) {
      console.error("Failed to persist automation state:", error);
    }
  };

  const loadPersistedRunState = async () => {
    try {
      const response = await fetch("/api/settings?key=automation_run_state");
      if (!response.ok) {
        setPersistedRunState(null);
        return null;
      }

      const data = await response.json();
      const rawValue = typeof data?.value === "string" ? data.value : "";
      if (!rawValue) {
        setPersistedRunState(null);
        return null;
      }

      const parsed = JSON.parse(rawValue) as PersistedAutomationState;
      setPersistedRunState(parsed);
      return parsed;
    } catch (error) {
      console.error("Failed to load automation state:", error);
      setPersistedRunState(null);
      return null;
    }
  };

  const waitFor = async (ms: number) => {
    const intervalMs = 250;
    let remaining = ms;

    while (remaining > 0) {
      if (stopActionRef.current) {
        const stopError = new Error(
          stopActionRef.current === "pause" ? "Automation paused." : "Automation cancelled."
        );
        stopError.name = stopActionRef.current === "pause" ? "PauseRequested" : "CancelRequested";
        throw stopError;
      }

      const chunk = Math.min(intervalMs, remaining);
      await new Promise((resolve) => setTimeout(resolve, chunk));
      remaining -= chunk;
    }
  };

  const matchesRelevantDomain = (log: any) => {
    const relevantDomains = runAllDomains && allDomains.length > 0
      ? allDomains.map((d) => d.url)
      : (domain ? [domain.url] : []);

    const logUrl = log?.domain?.url || log?.url || "";

    return relevantDomains.some((domainUrl) =>
      logUrl.includes(domainUrl) ||
      domainUrl.includes(logUrl) ||
      logUrl === domainUrl
    );
  };

  const stopActiveAutomation = async (action: "pause" | "cancel") => {
    stopActionRef.current = action;

    if (abortController) {
      abortController.abort();
    }

    const submissionIds = new Set<number>();

    if (currentSubmissionIdRef.current) {
      submissionIds.add(currentSubmissionIdRef.current);
    }

    try {
      const response = await fetch("/api/logs?status=running&limit=100");
      if (response.ok) {
        const data = await response.json();
        const relevantLogs = (data.logs || []).filter((log: any) => matchesRelevantDomain(log));
        for (const log of relevantLogs) {
          if (typeof log.id === "number") {
            submissionIds.add(log.id);
          }
        }
      }
    } catch (error) {
      console.error("Failed to load running submissions before stop:", error);
    }

    await Promise.all(
      Array.from(submissionIds).map(async (submissionId) => {
        try {
          await fetch("/api/run", {
            method: "DELETE",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ submissionId, action }),
          });
        } catch (error) {
          console.error(`Failed to ${action} submission ${submissionId}:`, error);
        }
      })
    );

    currentSubmissionIdRef.current = null;
  };

  // Simple elapsed time counter (only when running)
  useEffect(() => {
    if (!isRunning || !startTime) return;
    
    const interval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime.getTime()) / 1000);
      const hours = Math.floor(elapsed / 3600);
      const minutes = Math.floor((elapsed % 3600) / 60);
      const seconds = elapsed % 60;
      
      if (hours > 0) {
        setElapsedTime(`${hours}h ${minutes}m ${seconds}s`);
      } else if (minutes > 0) {
        setElapsedTime(`${minutes}m ${seconds}s`);
      } else {
        setElapsedTime(`${seconds}s`);
      }
    }, 1000);
    
    return () => clearInterval(interval);
  }, [isRunning, startTime]);

  // Check for running submissions on mount and periodically
  useEffect(() => {
    const checkRunningSubmissions = async () => {
      try {
        const storedState = await loadPersistedRunState();
        // First, check if we have saved progress and running logs
        const response = await fetch("/api/logs?status=running&limit=100");
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
                
                // Set start time from the earliest running log
                if (latestRunning?.createdAt) {
                  setStartTime(new Date(latestRunning.createdAt));
                }
              }
              
              // Extract and update message from log
              const logMessage = latestRunning?.message || "";
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
                  const domainUrl = latestRunning?.domain?.url || latestRunning?.url || "domain";
                  setMessage(`Running automation for ${domainUrl}...`);
                }
              } else {
                // Fallback message
                const domainUrl = latestRunning?.domain?.url || latestRunning?.url || "domain";
                setMessage(`Running automation for ${domainUrl}...`);
              }
              
              // Set last run time
              if (latestRunning?.createdAt) {
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
            } else if (storedState?.status === "running") {
              const interruptedState: PersistedAutomationState = {
                ...storedState,
                status: "interrupted",
                message: storedState.message || "Run was interrupted. Resume from stored state.",
                lastUpdatedAt: new Date().toISOString(),
              };
              setIsRunning(false);
              setStatus("idle");
              setMessage(interruptedState.message);
              setStartTime(storedState.startedAt ? new Date(storedState.startedAt) : null);
              setCurrentBatch(storedState.currentBatch || 0);
              setTotalBatches(storedState.totalBatches || 0);
              await savePersistedRunState(interruptedState);
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
            } else if (storedState?.status === "running") {
              const interruptedState: PersistedAutomationState = {
                ...storedState,
                status: "interrupted",
                message: storedState.message || "Run was interrupted. Resume from stored state.",
                lastUpdatedAt: new Date().toISOString(),
              };
              setIsRunning(false);
              setStatus("idle");
              setMessage(interruptedState.message);
              await savePersistedRunState(interruptedState);
            }
          }
        }
      } catch (error) {
        console.error("Failed to check running submissions:", error);
      }
    };

    // Check immediately on mount
    checkRunningSubmissions();

    // Adaptive polling with Page Visibility API
    // Note: isPageVisible and lastActivityTime are defined at component top level
    let timeoutId: NodeJS.Timeout | null = null;
    
    const handleVisibilityChange = () => {
      isPageVisible.current = !document.hidden;
    };
    document.addEventListener("visibilitychange", handleVisibilityChange);
    
    const getPollInterval = () => {
      const timeSinceActivity = Date.now() - lastActivityTime.current;
      // Fast polling (2s) when active, slower (10s) when idle
      return timeSinceActivity < 30000 ? 2000 : 10000;
    };
    
    const poll = () => {
      if (isPageVisible.current) {
        checkRunningSubmissions();
        lastActivityTime.current = Date.now();
        timeoutId = setTimeout(poll, getPollInterval());
      }
    };
    
    // Start polling
    timeoutId = setTimeout(poll, getPollInterval());

    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [domain, allDomains, status, isRunning, runAllDomains]);

  const primaryTemplate = domain?.templates?.[0];
  // Filter to only domains with contact page URL and forms found
  // When runAllDomains is true, use all domains with contact page URL and forms found (they'll be filtered during execution)
  // When false, only use the primary domain (which has contact page URL, templates and forms found)
  const domainsWithContactPage = allDomains.filter(d => d.contactPageUrl && d.contactCheckStatus === "found");
  const domainsToRun = runAllDomains && domainsWithContactPage.length > 0 
    ? domainsWithContactPage 
    : (domain && domain.contactPageUrl && domain.contactCheckStatus === "found" ? [domain] : []);
  
  // Debug logging
  if (runAllDomains) {
    const domainsWithTemplates = domainsWithContactPage.filter((d: DomainWithTemplate) => d.templates.length > 0);
    console.log(`[AutomationControls] Run all domains enabled. Total domains with contact pages and forms: ${domainsWithContactPage.length}, Domains with templates: ${domainsWithTemplates.length}`);
  }

  // Can run if:
  // - Not currently running
  // - Has at least one domain to run with contact page URL and forms found
  // - If runAllDomains is false, the primary domain must have contact page URL, templates and forms found
  // - If runAllDomains is true, at least one domain must have contact page URL, templates and forms found
  const hasRunnableDomains = runAllDomains 
    ? domainsWithContactPage.some((d: DomainWithTemplate) => d.templates.length > 0 && d.isActive && d.contactPageUrl && d.contactCheckStatus === "found")
    : (domain && domain.templates.length > 0 && domain.isActive && domain.contactPageUrl && domain.contactCheckStatus === "found");
  const canRun = Boolean(domainsToRun.length > 0 && hasRunnableDomains && !isRunning);

  const handleStartRun = async (options: StartRunOptions = {}) => {
    const { isTest = false, restartMode = false, resumeStoredState = false } = options;
    let initialRunMessage: string | null = null;

    if (domainsToRun.length === 0) {
      alert("No domains available to run.");
      return;
    }
    
    if (isRunning) {
      alert("⚠️ Automation is already running. Please wait for it to complete, pause it, or cancel it before starting a new run.");
      return;
    }

    // Filter to only domains with contact page URL, templates, and forms found
    let domainsToProcess = domainsToRun.filter(d => 
      d.contactPageUrl && 
      d.templates.length > 0 && 
      d.contactCheckStatus === "found"
    );

    let resumedState: PersistedAutomationState | null = null;
    if (resumeStoredState) {
      resumedState = persistedRunState ?? await loadPersistedRunState();
      if (!resumedState || resumedState.pendingDomainIds.length === 0) {
        alert("No stored run state found to resume.");
        return;
      }

      const pendingIdSet = new Set(resumedState.pendingDomainIds);
      domainsToProcess = domainsToProcess.filter((domainItem) => pendingIdSet.has(domainItem.id));

      if (domainsToProcess.length === 0) {
        alert("Stored run exists, but no pending domains are currently available to resume.");
        return;
      }

      initialRunMessage = `Resuming stored run with ${domainsToProcess.length} remaining domain(s).`;
    }

    if (restartMode) {
      try {
        const response = await fetch("/api/logs?limit=1000");
        if (response.ok) {
          const data = await response.json();
          const relevantLogs = (data.logs || []).filter((log: any) => matchesRelevantDomain(log));
          const terminalStatuses = new Set(["success", "failed", "submitted", "completed", "cancelled", "paused"]);
          const completedByDomain = new Set<string>();

          for (const log of relevantLogs) {
            const domainUrl = log?.domain?.url || "";
            if (!domainUrl || completedByDomain.has(domainUrl)) continue;
            if (terminalStatuses.has(String(log.status || "").toLowerCase())) {
              completedByDomain.add(domainUrl);
            }
          }

          const remainingDomains = domainsToProcess.filter((domainItem) => !completedByDomain.has(domainItem.url));
          const skippedCount = domainsToProcess.length - remainingDomains.length;

          if (remainingDomains.length === 0) {
            setStatus("success");
            setMessage(
              skippedCount > 0
                ? `Restart skipped all ${skippedCount} domain(s) because they already have completed logs.`
                : "No remaining domains found to restart."
            );
            setIsRunning(false);
            setIsPaused(false);
            return;
          }

          domainsToProcess = remainingDomains;
          initialRunMessage = `Restarting ${remainingDomains.length} remaining domain(s). Skipping ${skippedCount} already completed domain(s).`;
        }
      } catch (error) {
        console.error("Failed to load logs for restart mode:", error);
      }
    }

    setStatus("running");
    setMessage(initialRunMessage);
    setIsRunning(true);
    setIsPaused(false);
    stopActionRef.current = null;
    currentSubmissionIdRef.current = null;
    
    // Initialize batch tracking
    const actualBatchesCount = Math.ceil(domainsToProcess.length / batchSize);
    setTotalBatches(actualBatchesCount);
    setCurrentBatch(0);
    setAverageTimePerDomain(0);
    
    // Start time tracking
    const runStartTime = new Date();
    setStartTime(runStartTime);
    setElapsedTime("0s");

    const persistedStateBase: PersistedAutomationState = {
      status: "running",
      isTest,
      runAllDomains,
      batchSize,
      delaySeconds,
      retryLimit,
      startedAt: resumedState?.startedAt || runStartTime.toISOString(),
      lastUpdatedAt: new Date().toISOString(),
      totalDomains: resumedState?.totalDomains || domainsToProcess.length,
      processedDomains: resumedState?.processedDomains || 0,
      currentBatch: 0,
      totalBatches: actualBatchesCount,
      currentDomainId: null,
      currentDomainUrl: null,
      pendingDomainIds: domainsToProcess.map((d) => d.id),
      completedDomainIds: resumedState?.completedDomainIds || [],
      failedDomainIds: resumedState?.failedDomainIds || [],
      skippedDomainIds: resumedState?.skippedDomainIds || [],
      message: initialRunMessage,
    };
    await savePersistedRunState(persistedStateBase);

    const controller = new AbortController();
    setAbortController(controller);
    
    // Set timeout to 6 minutes per domain (slightly longer than API timeout of 5 minutes)
    const timeoutPerDomain = 6 * 60 * 1000;
    const totalTimeout = timeoutPerDomain * domainsToProcess.length;
    const timeoutId = setTimeout(() => {
      controller.abort();
    }, totalTimeout);

    try {
      const results: Array<{ domain: string; success: boolean; message: string }> = [];
      
      // Run automation for each domain in batches
      console.log(`[AutomationControls] Starting batch run for ${domainsToProcess.length} domain(s) with contact pages in batches of ${batchSize}:`, domainsToProcess.map(d => d.contactPageUrl || d.url));
      
      let processedCount = 0;
      let totalProcessed = 0;
      
      // Process in batches
      for (let batchIndex = 0; batchIndex < actualBatchesCount; batchIndex++) {
        const batchStart = batchIndex * batchSize;
        const batchEnd = Math.min(batchStart + batchSize, domainsToProcess.length);
        const batchDomains = domainsToProcess.slice(batchStart, batchEnd);
        
        setCurrentBatch(batchIndex + 1);
        setMessage(`Processing batch ${batchIndex + 1}/${actualBatchesCount} (${batchDomains.length} domains)...`);
        await savePersistedRunState({
          ...(persistedRunState ?? persistedStateBase),
          status: "running",
          currentBatch: batchIndex + 1,
          totalBatches: actualBatchesCount,
          lastUpdatedAt: new Date().toISOString(),
          message: `Processing batch ${batchIndex + 1}/${actualBatchesCount} (${batchDomains.length} domains)...`,
        });
        
        console.log(`[AutomationControls] Processing batch ${batchIndex + 1}/${actualBatchesCount}: ${batchDomains.length} domains`);
        
        // Process each domain in the current batch
        for (let i = 0; i < batchDomains.length; i++) {
          const currentDomain = batchDomains[i];
        const currentTemplate = currentDomain.templates[0];
        
        // Skip domains without contact page URL found
        if (!currentDomain.contactPageUrl) {
          console.warn(`[AutomationControls] Domain ${currentDomain.url} has no contact page URL found, skipping`);
          results.push({
            domain: currentDomain.url,
            success: false,
            message: `No contact page URL found. Only domains with contact pages can be run.`
          });
          continue;
        }
        
        // Skip domains without forms found
        if (currentDomain.contactCheckStatus !== "found") {
          console.warn(`[AutomationControls] Domain ${currentDomain.url} has no form found (status: ${currentDomain.contactCheckStatus}), skipping`);
          results.push({
            domain: currentDomain.url,
            success: false,
            message: `No form found on contact page (status: ${currentDomain.contactCheckStatus}). Only domains with forms found can be run.`
          });
          continue;
        }
        
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
          totalProcessed++;
          
          // Calculate static average time per domain
          if (totalProcessed > 0 && runStartTime) {
            const elapsed = Math.floor((Date.now() - runStartTime.getTime()) / 1000);
            const avgTime = elapsed / totalProcessed;
            setAverageTimePerDomain(avgTime);
          }
          
          const batchProgress = `Batch ${batchIndex + 1}/${actualBatchesCount}`;
          const overallProgress = `(${totalProcessed}/${domainsToProcess.length})`;
          setMessage(`${batchProgress} - Running automation for ${currentDomain.contactPageUrl} ${overallProgress}...`);
          const latestBeforeRun = await loadPersistedRunState();
          await savePersistedRunState({
            ...(latestBeforeRun ?? persistedStateBase),
            status: "running",
            currentBatch: batchIndex + 1,
            totalBatches: actualBatchesCount,
            currentDomainId: currentDomain.id,
            currentDomainUrl: currentDomain.contactPageUrl || currentDomain.url,
            lastUpdatedAt: new Date().toISOString(),
            message: `${batchProgress} - Running automation for ${currentDomain.contactPageUrl} ${overallProgress}...`,
          });

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

          // Use contact page URL if available, otherwise fall back to domain URL
          const targetUrl = currentDomain.contactPageUrl || currentDomain.url;
          
          const response = await fetch("/api/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              url: targetUrl,
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
              currentSubmissionIdRef.current = submissionId;
              const batchProgress = `Batch ${batchIndex + 1}/${actualBatchesCount}`;
              const overallProgress = `(${totalProcessed}/${domainsToProcess.length})`;
              setMessage(`${batchProgress} - Waiting for ${currentDomain.contactPageUrl} to complete ${overallProgress}...`);
              
              // Update average time per domain
              if (totalProcessed > 0 && runStartTime) {
                const elapsed = Math.floor((Date.now() - runStartTime.getTime()) / 1000);
                const avgTime = elapsed / totalProcessed;
                setAverageTimePerDomain(avgTime);
              }
              
              // Poll for completion (check every 2 seconds, max 10 minutes per domain)
              let completed = false;
              const maxWaitTime = 10 * 60 * 1000; // 10 minutes
              const startTime = Date.now();
              const pollInterval = 2000; // 2 seconds
              
              while (!completed && (Date.now() - startTime) < maxWaitTime) {
                if (stopActionRef.current) {
                  const stopError = new Error(
                    stopActionRef.current === "pause" ? "Automation paused." : "Automation cancelled."
                  );
                  stopError.name = stopActionRef.current === "pause" ? "PauseRequested" : "CancelRequested";
                  throw stopError;
                }

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
                        const latestState = await loadPersistedRunState();
                        if (latestState) {
                          const successful = submission.status === "success" || submission.status === "submitted" || submission.status === "completed";
                          await savePersistedRunState({
                            ...latestState,
                            status: "running",
                            processedDomains: latestState.processedDomains + 1,
                            currentDomainId: null,
                            currentDomainUrl: null,
                            pendingDomainIds: latestState.pendingDomainIds.filter((id) => id !== currentDomain.id),
                            completedDomainIds: successful
                              ? Array.from(new Set([...latestState.completedDomainIds, currentDomain.id]))
                              : latestState.completedDomainIds,
                            failedDomainIds: successful
                              ? latestState.failedDomainIds
                              : Array.from(new Set([...latestState.failedDomainIds, currentDomain.id])),
                            lastUpdatedAt: new Date().toISOString(),
                            message: submission.message || `Run ${submission.status}`,
                          });
                        }
                        currentSubmissionIdRef.current = null;
                        break;
                      }
                      // Still running, update message
                      if (submission.message) {
                        const lines = submission.message.split("\n");
                        const lastLine = lines[lines.length - 1] || lines[0] || "";
                        if (lastLine.trim()) {
                          const batchProgress = `Batch ${batchIndex + 1}/${actualBatchesCount}`;
                          const overallProgress = `(${totalProcessed}/${domainsToProcess.length})`;
                          setMessage(`${batchProgress} - ${currentDomain.contactPageUrl} ${overallProgress}: ${lastLine.substring(0, 80)}...`);
                        }
                      }
                    }
                  }
                  
                  // Wait before next poll
                  await waitFor(pollInterval);
                } catch (pollError) {
                  if (
                    pollError instanceof Error &&
                    (pollError.name === "PauseRequested" || pollError.name === "CancelRequested")
                  ) {
                    throw pollError;
                  }
                  console.error("Error polling for completion:", pollError);
                  // Continue polling
                  await waitFor(pollInterval);
                }
              }
              
              if (!completed) {
                results.push({
                  domain: currentDomain.url,
                  success: false,
                  message: "Automation timed out (waited 10 minutes)"
                });
                const latestState = await loadPersistedRunState();
                if (latestState) {
                  await savePersistedRunState({
                    ...latestState,
                    status: "running",
                    processedDomains: latestState.processedDomains + 1,
                    currentDomainId: null,
                    currentDomainUrl: null,
                    pendingDomainIds: latestState.pendingDomainIds.filter((id) => id !== currentDomain.id),
                    failedDomainIds: Array.from(new Set([...latestState.failedDomainIds, currentDomain.id])),
                    lastUpdatedAt: new Date().toISOString(),
                    message: "Automation timed out (waited 10 minutes)",
                  });
                }
              }
            } else {
              results.push({
                domain: currentDomain.url,
                success: true,
                message: payload?.message ?? "Run started successfully."
              });
            }
          }

          // Add delay between domains to avoid rate limiting (only if not the last domain in batch)
          if (i < batchDomains.length - 1) {
            setMessage(`Batch ${batchIndex + 1}/${actualBatchesCount} - Waiting ${delaySeconds} seconds before next domain...`);
            await waitFor(delaySeconds * 1000);
          }
        } catch (error) {
          if (error instanceof Error && error.name === "AbortError") {
            throw error; // Re-throw abort to break the loop
          }
          if (error instanceof Error && (error.name === "PauseRequested" || error.name === "CancelRequested")) {
            throw error;
          }
          results.push({
            domain: currentDomain.url,
            success: false,
            message: error instanceof Error ? error.message : "Unknown error"
          });
          const latestState = await loadPersistedRunState();
          if (latestState) {
            await savePersistedRunState({
              ...latestState,
              status: "running",
              processedDomains: latestState.processedDomains + 1,
              currentDomainId: null,
              currentDomainUrl: null,
              pendingDomainIds: latestState.pendingDomainIds.filter((id) => id !== currentDomain.id),
              failedDomainIds: Array.from(new Set([...latestState.failedDomainIds, currentDomain.id])),
              lastUpdatedAt: new Date().toISOString(),
              message: error instanceof Error ? error.message : "Unknown error",
            });
          }
        }
        }
        
        // Add delay between batches (except for the last batch)
        if (batchIndex < actualBatchesCount - 1) {
          setMessage(`Batch ${batchIndex + 1}/${actualBatchesCount} completed. Waiting ${delaySeconds * 2} seconds before next batch...`);
          await waitFor(delaySeconds * 2 * 1000);
        }
      }

      clearTimeout(timeoutId);

      // Calculate total time taken
      const endTime = new Date();
      const totalTimeMs = endTime.getTime() - runStartTime.getTime();
      const totalTimeSeconds = Math.floor(totalTimeMs / 1000);
      const hours = Math.floor(totalTimeSeconds / 3600);
      const minutes = Math.floor((totalTimeSeconds % 3600) / 60);
      const seconds = totalTimeSeconds % 60;
      let timeTaken = "";
      if (hours > 0) {
        timeTaken = `${hours}h ${minutes}m ${seconds}s`;
      } else if (minutes > 0) {
        timeTaken = `${minutes}m ${seconds}s`;
      } else {
        timeTaken = `${seconds}s`;
      }

      // Summarize results
      const successCount = results.filter(r => r.success).length;
      const failureCount = results.filter(r => !r.success).length;
      
      if (failureCount === 0) {
        setStatus("success");
        setMessage(
          isTest 
            ? `Test completed successfully for all ${domainsToProcess.length} domain(s) with contact pages in ${actualBatchesCount} batch(es). Time taken: ${timeTaken}. Check the browser window to verify submissions.`
            : `All ${domainsToProcess.length} domain(s) with contact pages completed successfully in ${actualBatchesCount} batch(es). Time taken: ${timeTaken}.`
        );
      } else if (successCount === 0) {
        setStatus("error");
        setMessage(`All ${domainsToProcess.length} domain(s) with contact pages failed. Time taken: ${timeTaken}. Check logs for details.`);
      } else {
        setStatus("success");
        setMessage(`${successCount} succeeded, ${failureCount} failed out of ${domainsToProcess.length} domain(s) with contact pages in ${actualBatchesCount} batch(es). Time taken: ${timeTaken}.`);
      }
      
      setElapsedTime(timeTaken);
      setLastRun(new Date());
      setIsRunning(false);
      setIsPaused(false);
      setAbortController(null);
      setCurrentBatch(0);
      setTotalBatches(0);
      setStartTime(null);
      setAverageTimePerDomain(0);
      const latestState = await loadPersistedRunState();
      await savePersistedRunState({
        ...(latestState ?? persistedStateBase),
        status: "completed",
        currentDomainId: null,
        currentDomainUrl: null,
        pendingDomainIds: [],
        lastUpdatedAt: new Date().toISOString(),
        message:
          failureCount === 0
            ? `Run completed successfully.`
            : `${successCount} succeeded and ${failureCount} failed.`,
      });
    } catch (error) {
      clearTimeout(timeoutId);
      
      // Calculate elapsed time even on error
      if (runStartTime) {
        const endTime = new Date();
        const totalTimeMs = endTime.getTime() - runStartTime.getTime();
        const totalTimeSeconds = Math.floor(totalTimeMs / 1000);
        const hours = Math.floor(totalTimeSeconds / 3600);
        const minutes = Math.floor((totalTimeSeconds % 3600) / 60);
        const seconds = totalTimeSeconds % 60;
        let timeTaken = "";
        if (hours > 0) {
          timeTaken = `${hours}h ${minutes}m ${seconds}s`;
        } else if (minutes > 0) {
          timeTaken = `${minutes}m ${seconds}s`;
        } else {
          timeTaken = `${seconds}s`;
        }
        setElapsedTime(timeTaken);
      }
      
      const requestedStop = stopActionRef.current;

      if (
        (error instanceof Error && error.name === "PauseRequested") ||
        (error instanceof Error && error.name === "AbortError" && requestedStop === "pause")
      ) {
        setStatus("idle");
        setMessage(`Automation run paused. Elapsed time: ${elapsedTime || "0s"}.`);
        setIsPaused(true);
        const latestState = await loadPersistedRunState();
        if (latestState) {
          await savePersistedRunState({
            ...latestState,
            status: "paused",
            currentDomainId: null,
            currentDomainUrl: null,
            lastUpdatedAt: new Date().toISOString(),
            message: `Automation run paused. Elapsed time: ${elapsedTime || "0s"}.`,
          });
        }
      } else if (
        (error instanceof Error && error.name === "CancelRequested") ||
        (error instanceof Error && error.name === "AbortError" && requestedStop === "cancel")
      ) {
        setStatus("idle");
        setMessage(`Automation run cancelled. Elapsed time: ${elapsedTime || "0s"}.`);
        setIsPaused(false);
        const latestState = await loadPersistedRunState();
        if (latestState) {
          await savePersistedRunState({
            ...latestState,
            status: "cancelled",
            currentDomainId: null,
            currentDomainUrl: null,
            lastUpdatedAt: new Date().toISOString(),
            message: `Automation run cancelled. Elapsed time: ${elapsedTime || "0s"}.`,
          });
        }
      } else {
        setStatus("error");
        if (error instanceof Error) {
          if (error.name === "AbortError") {
            setMessage(`Request timed out. Elapsed time: ${elapsedTime || "0s"}. The automation may still be running in the background. Check the logs for status.`);
          } else {
            setMessage(`${error.message}. Elapsed time: ${elapsedTime || "0s"}.`);
          }
        } else {
          setMessage(`Unable to start automation run. Elapsed time: ${elapsedTime || "0s"}.`);
        }
        const latestState = await loadPersistedRunState();
        if (latestState) {
          await savePersistedRunState({
            ...latestState,
            status: "interrupted",
            currentDomainId: null,
            currentDomainUrl: null,
            lastUpdatedAt: new Date().toISOString(),
            message:
              error instanceof Error
                ? `${error.message}. Elapsed time: ${elapsedTime || "0s"}.`
                : `Unable to start automation run. Elapsed time: ${elapsedTime || "0s"}.`,
          });
        }
      }
      setIsRunning(false);
      currentSubmissionIdRef.current = null;
      setAbortController(null);
      setCurrentBatch(0);
      setTotalBatches(0);
      setStartTime(null);
      setAverageTimePerDomain(0);
      stopActionRef.current = null;
    }
  };

  const handlePause = async () => {
    if (isPaused) {
      // Resume - this would require restarting the process, which is complex
      // For now, just show a message that resuming requires restarting
      alert("To resume, please start a new run. The system will skip already processed domains if you use the same domain list.");
      return;
    }
    
    if (isRunning) {
      await stopActiveAutomation("pause");
    }
  };

  const handleCancel = async () => {
    if (!confirm("⚠️ Are you sure you want to cancel the current automation run? Progress will be lost.")) {
      return;
    }

    if (isRunning) {
      await stopActiveAutomation("cancel");
    }
  };

  const handleTestDomain = () => {
    handleStartRun({ isTest: true });
  };

  const handleRestartRun = () => {
    handleStartRun({ restartMode: true });
  };

  const handleResumeStoredRun = () => {
    handleStartRun({ resumeStoredState: true, isTest: persistedRunState?.isTest ?? false });
  };

  const handleRecheckAllContacts = async () => {
    if (recheckingContacts) return;
    
    const allDomainIds = allDomains.map(d => d.id);
    const count = allDomainIds.length;
    
    const message = `Re-check contact pages for ALL ${count} domain(s)? This may take a very long time.`;
    
    if (!confirm(message)) {
      return;
    }
    
    setRecheckingContacts(true);
    try {
      const response = await fetch("/api/domains/check-contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ domainIds: allDomainIds }),
      });

      if (response.ok) {
        const data = await response.json();
        setMessage(`Contact page re-check completed: ${data.message}`);
        setStatus("success");
        // Refresh domains by triggering a page reload or state update
        window.location.reload();
      } else {
        const error = await response.json();
        setMessage(`Failed to re-check contact pages: ${error.detail || "Unknown error"}`);
        setStatus("error");
      }
    } catch (error: any) {
      console.error("Failed to re-check all contact pages:", error);
      setMessage(`Failed to re-check all contact pages: ${error.message || "Unknown error"}`);
      setStatus("error");
    } finally {
      setRecheckingContacts(false);
    }
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
              ? runAllDomains && domainsWithContactPage.length > 1
                ? `Running on ${domainsWithContactPage.length} domain(s) with contact pages and forms found`
                : `Primary domain: ${domain?.contactPageUrl || domain?.url}${primaryTemplate ? ` • Template: ${primaryTemplate.name}` : ""}`
              : "No domains with contact pages and forms found and templates available."}
          </p>
          {domainsWithContactPage.length > 1 && (
            <div className="mt-2 space-y-1">
              <label className="flex items-center gap-2 text-xs text-slate-300">
                <input
                  type="checkbox"
                  checked={runAllDomains}
                  onChange={(e) => {
                    setRunAllDomains(e.target.checked);
                    if (e.target.checked) {
                      const domainsWithTemplates = domainsWithContactPage.filter(d => d.templates.length > 0);
                      const domainsWithoutTemplates = domainsWithContactPage.filter(d => d.templates.length === 0);
                      let msg = `Will run on ${domainsWithTemplates.length} domain(s) with contact pages, forms found and templates`;
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
                <span>Run on all {domainsWithContactPage.length} domains with contact pages and forms found</span>
              </label>
              {runAllDomains && (
                <div className="ml-6 text-xs text-slate-400">
                  <div>• {domainsWithContactPage.filter(d => d.templates.length > 0).length} with templates: {domainsWithContactPage.filter(d => d.templates.length > 0).slice(0, 5).map(d => (d.contactPageUrl || d.url).split('/')[2] || (d.contactPageUrl || d.url)).join(', ')}{domainsWithContactPage.filter(d => d.templates.length > 0).length > 5 ? '...' : ''}</div>
                  {domainsWithContactPage.filter(d => d.templates.length === 0).length > 0 && (
                    <div className="text-amber-400">• {domainsWithContactPage.filter(d => d.templates.length === 0).length} without templates (will be skipped): {domainsWithContactPage.filter(d => d.templates.length === 0).slice(0, 5).map(d => (d.contactPageUrl || d.url).split('/')[2] || (d.contactPageUrl || d.url)).join(', ')}{domainsWithContactPage.filter(d => d.templates.length === 0).length > 5 ? '...' : ''}</div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => handleStartRun()}
            disabled={!canRun || isRunning || recheckingContacts}
            className="rounded-lg bg-indigo-500 px-4 py-2 text-xs font-medium text-white hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-60 transition-colors"
          >
            {status === "running" || isRunning ? "Running…" : "Start Run"}
          </button>
          {isRunning && (
            <>
              <button
                type="button"
                onClick={handlePause}
                disabled={isPaused}
                className="rounded-lg border border-yellow-600 px-4 py-2 text-xs font-medium text-yellow-300 hover:bg-yellow-600/20 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title={isPaused ? "Run is paused. Start a new run to continue." : "Pause the current automation run"}
              >
                Pause
              </button>
              <button
                type="button"
                onClick={handleCancel}
                className="rounded-lg border border-rose-600 px-4 py-2 text-xs font-medium text-rose-300 hover:bg-rose-600/20 transition-colors"
                title="Cancel the current automation run (progress will be lost)"
              >
                Cancel
              </button>
            </>
          )}
          {!isRunning && (
            <>
              <button
                type="button"
                disabled={!canRun}
                onClick={handleTestDomain}
                className="rounded-lg border border-slate-700 px-4 py-2 text-xs font-medium text-slate-200 hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60 transition-colors"
              >
                Test Domain
              </button>
              <button
                type="button"
                disabled={!canRun}
                onClick={handleRestartRun}
                className="rounded-lg border border-emerald-600 px-4 py-2 text-xs font-medium text-emerald-300 hover:bg-emerald-600/20 disabled:cursor-not-allowed disabled:opacity-60 transition-colors"
                title="Start a new run and skip domains that already have completed logs"
              >
                Restart Run
              </button>
              <button
                type="button"
                disabled={!persistedRunState || !["paused", "interrupted", "cancelled", "running"].includes(persistedRunState.status) || persistedRunState.pendingDomainIds.length === 0}
                onClick={handleResumeStoredRun}
                className="rounded-lg border border-cyan-600 px-4 py-2 text-xs font-medium text-cyan-300 hover:bg-cyan-600/20 disabled:cursor-not-allowed disabled:opacity-60 transition-colors"
                title="Resume remaining domains from the last stored run state in the database"
              >
                Resume Stored Run
              </button>
              <button
                type="button"
                onClick={handleRecheckAllContacts}
                disabled={recheckingContacts || allDomains.length === 0}
                className="rounded-lg border border-blue-600 px-4 py-2 text-xs font-medium text-blue-400 hover:bg-blue-600/20 disabled:cursor-not-allowed disabled:opacity-60 transition-colors"
                title="Re-check contact pages for all domains"
              >
                {recheckingContacts ? "Rechecking…" : "Recheck All Contacts"}
              </button>
            </>
          )}
        </div>
      </div>


      <div className="mt-6 grid gap-4 rounded-xl border border-dashed border-slate-800 bg-slate-950/60 p-6 text-sm text-slate-400">
        <div className="flex justify-between">
          <span>Current status</span>
          <span className="text-indigo-300">{currentStatusLabel}</span>
        </div>
        {isRunning && totalBatches > 0 && (
          <div className="flex justify-between">
            <span>Batch progress</span>
            <span className="text-indigo-300">Batch {currentBatch}/{totalBatches}</span>
          </div>
        )}
        {isRunning && elapsedTime && (
          <div className="flex justify-between">
            <span>Elapsed time</span>
            <span className="text-emerald-300">{elapsedTime}</span>
          </div>
        )}
        {isRunning && averageTimePerDomain > 0 && (
          <div className="flex justify-between">
            <span>Avg. time per domain</span>
            <span className="text-slate-300">{Math.round(averageTimePerDomain)}s</span>
          </div>
        )}
        <div className="flex justify-between">
          <span>Delay</span>
          <span>{delaySeconds} seconds</span>
        </div>
        <div className="flex justify-between">
          <span>Batch size</span>
          <span>{batchSize} domains</span>
        </div>
        <div className="flex justify-between">
          <span>Retry limit</span>
          <span>{retryLimit} attempts</span>
        </div>
        <div className="flex justify-between">
          <span>Last run</span>
          <span>{lastRun ? lastRun.toLocaleString() : "Not yet run"}</span>
        </div>
        {persistedRunState && (
          <>
            <div className="flex justify-between">
              <span>Stored run state</span>
              <span className="text-cyan-300">{persistedRunState.status}</span>
            </div>
            <div className="flex justify-between">
              <span>Stored remaining</span>
              <span>{persistedRunState.pendingDomainIds.length} domains</span>
            </div>
          </>
        )}
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
