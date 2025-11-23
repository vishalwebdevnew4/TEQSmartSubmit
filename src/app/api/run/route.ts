import { NextRequest, NextResponse } from "next/server";
import { spawn } from "node:child_process";
import { mkdtemp, writeFile, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";

import { prisma } from "@/lib/prisma";

export const runtime = "nodejs";

export async function POST(req: NextRequest) {
  try {
    const { url, template, domainId, templateId, adminId, isTest } = await req.json();

    const normalizeId = (value: unknown) => {
      if (typeof value === "number" && Number.isInteger(value)) return value;
      if (typeof value === "string" && value.trim().length > 0) {
        const parsed = Number(value);
        if (!Number.isNaN(parsed) && Number.isInteger(parsed)) return parsed;
      }
      return null;
    };

    const domainIdValue = normalizeId(domainId);
    const templateIdValue = normalizeId(templateId);
    const adminIdValue = normalizeId(adminId);

    if (!url || typeof url !== "string") {
      return NextResponse.json(
        { status: "error", message: "Field 'url' is required." },
        { status: 400 }
      );
    }

    if (!template || typeof template !== "object") {
      return NextResponse.json(
        { status: "error", message: "Field 'template' must be an object." },
        { status: 400 }
      );
    }

    // Ensure local CAPTCHA solver is enabled by default and use ONLY local solver
    // Disable hybrid mode to prevent falling back to external services
    // For test mode, show browser (headless=false) so user can see what's happening
    // Enable auto-detect if no fields are provided
    const hasFields = template.fields && Array.isArray(template.fields) && template.fields.length > 0;
    
    // Check if we have a display available (for non-headless mode)
    // On remote servers without display, we need to use headless mode
    // Check for DISPLAY env var (X11) or if we're in a headless environment
    const hasDisplay = process.env.DISPLAY !== undefined && process.env.DISPLAY !== '';
    const forceHeadless = process.env.TEQ_FORCE_HEADLESS === 'true';
    
    // If template explicitly sets headless, use that; otherwise auto-detect
    // For sites with CAPTCHA issues, prefer visible browser (headless=false)
    const templateHeadless = template.headless ?? template.Headless;
    let shouldUseHeadless: boolean;
    
    if (templateHeadless !== undefined) {
      // Template explicitly sets headless mode
      shouldUseHeadless = templateHeadless;
    } else if (forceHeadless) {
      // Environment forces headless
      shouldUseHeadless = true;
    } else if (isTest) {
      // Test mode - always use visible browser
      shouldUseHeadless = false;
    } else {
      // Auto-detect: prefer visible browser for better CAPTCHA solving
      // Use headless only if no display available
      shouldUseHeadless = !hasDisplay;
    }
    
    // Enable virtual display for better CAPTCHA solving when headless
    // Virtual display allows browser to render on a virtual screen instead of requiring physical monitor
    const useVirtualDisplay = template.use_virtual_display ?? template.useVirtualDisplay ?? (process.env.TEQ_USE_VIRTUAL_DISPLAY === 'true');
    
    // Enable browser reuse mode (single tab, just navigate to new URLs)
    // Browser runs in background (headless=false with virtual display)
    const reuseBrowser = template.reuse_browser ?? template.reuseBrowser ?? false;
    
    const enhancedTemplate = {
      ...template,
      use_local_captcha_solver: template.use_local_captcha_solver ?? true,
      use_hybrid_captcha_solver: template.use_hybrid_captcha_solver ?? false, // Default to false - use ONLY local solver
      captcha_service: template.captcha_service ?? "local", // Default to local only
      // For reuse mode: headless=false but with virtual display (runs in background)
      // For normal mode: Prefer visible browser (headless=false) for better CAPTCHA solving
      // Only use headless if explicitly set or no display available
      headless: reuseBrowser ? false : shouldUseHeadless,
      use_virtual_display: reuseBrowser ? true : useVirtualDisplay, // Always use virtual display in reuse mode
      reuse_browser: reuseBrowser, // Enable browser reuse (single tab mode)
      use_auto_detect: template.use_auto_detect ?? (!hasFields), // Auto-detect if no fields provided
      test_data: template.test_data ?? {
        name: "TEQ QA User",
        email: "test@example.com",
        phone: "+1234567890",
        message: "This is an automated test submission.",
        subject: "Test Inquiry",
        company: "Test Company"
      }
    };

    const tempDir = await mkdtemp(path.join(os.tmpdir(), "teq-template-"));
    const templatePath = path.join(tempDir, "template.json");
    await writeFile(templatePath, JSON.stringify(enhancedTemplate, null, 2), "utf8");

    const scriptPath = path.join(process.cwd(), "automation", "run_submission.py");

    const submission = await prisma.submissionLog.create({
      data: {
        url,
        status: "running",
        message: "Automation started",
        domainId: domainIdValue,
        templateId: templateIdValue,
        adminId: adminIdValue,
      },
    });

    // Use 'python' on Windows, 'python3' on Linux/Mac
    const pythonCommand = os.platform() === "win32" ? "python" : "python3";
    
    // Return immediately with submission ID - let automation run in background
    // This prevents the API from timing out while automation is running
    (async () => {
      try {
        const python = spawn(pythonCommand, [scriptPath, "--url", url, "--template", templatePath], {
          cwd: process.cwd(),
          env: { ...process.env, PYTHONUNBUFFERED: "1", PYTHONIOENCODING: "utf-8" },
        });

        python.stdout.setEncoding("utf8");
        python.stderr.setEncoding("utf8");

        let stdout = "";
        let stderr = "";
        let lastLogUpdate = Date.now();
        const LOG_UPDATE_INTERVAL = 2000; // Update database every 2 seconds with logs

        python.stdout.on("data", (chunk) => {
          stdout += chunk;
        });

        python.stderr.on("data", async (chunk) => {
          stderr += chunk;
          // Update database periodically with stderr logs so they appear in real-time
          const now = Date.now();
          if (now - lastLogUpdate > LOG_UPDATE_INTERVAL) {
            lastLogUpdate = now;
            try {
              // Store complete stderr logs (no truncation) for real-time viewing
              // Database Text field can handle large logs
              await prisma.submissionLog.update({
                where: { id: submission.id },
                data: {
                  message: stderr || "Automation in progress...",
                },
              });
            } catch (updateError) {
              // Ignore update errors to avoid breaking the main flow
              console.error("Failed to update log:", updateError);
            }
          }
        });

        // Add timeout (5 minutes for automation to complete)
        const TIMEOUT_MS = 5 * 60 * 1000; // 5 minutes
        const timeoutId = setTimeout(() => {
          python.kill("SIGTERM");
          // Force kill after 10 seconds if still running
          setTimeout(() => {
            if (!python.killed) {
              python.kill("SIGKILL");
            }
          }, 10000);
        }, TIMEOUT_MS);

        const exitCode: number = await new Promise((resolve, reject) => {
          python.on("error", (error) => {
            clearTimeout(timeoutId);
            reject(error);
          });
          python.on("close", (code) => {
            clearTimeout(timeoutId);
            resolve(code ?? 0);
          });
        });

        await rm(tempDir, { recursive: true, force: true }).catch(() => undefined);

    // Try to extract JSON from stdout (might be mixed with logs)
    let parsed: any = null;
    let jsonStart = -1;
    let jsonEnd = -1;
    
    // Look for JSON object in stdout (could be at the end or middle)
    const stdoutTrimmed = stdout.trim();
    
    // Try to find JSON object boundaries
    jsonStart = stdoutTrimmed.lastIndexOf("{");
    if (jsonStart !== -1) {
      // Find matching closing brace
      let braceCount = 0;
      for (let i = jsonStart; i < stdoutTrimmed.length; i++) {
        if (stdoutTrimmed[i] === "{") braceCount++;
        if (stdoutTrimmed[i] === "}") {
          braceCount--;
          if (braceCount === 0) {
            jsonEnd = i + 1;
            break;
          }
        }
      }
    }
    
    // Extract JSON if found
    if (jsonStart !== -1 && jsonEnd !== -1) {
      try {
        const jsonStr = stdoutTrimmed.substring(jsonStart, jsonEnd);
        parsed = JSON.parse(jsonStr);
      } catch (e) {
        // JSON parse failed, will handle below
      }
    }

    // If we found valid JSON, use it regardless of exit code
    if (parsed && typeof parsed === "object") {
      const finalStatus = parsed.status === "success" ? "success" : parsed.status || (exitCode === 0 ? "success" : "failed");
      // Include complete stderr logs in the final message (no truncation)
      // Combine stderr (main logs) with stdout (JSON output) for complete log
      const completeLogs = stderr.trim() || stdoutTrimmed || "";
      const finalMessage = completeLogs || parsed.message || null;
      
      await prisma.submissionLog.update({
        where: { id: submission.id },
        data: {
          status: finalStatus,
          message: finalMessage,
          finishedAt: new Date(),
        },
      });
      
      // Status already updated in database - no need to return here
    }

    // If exit code is non-zero and no JSON found, treat as error
    if (exitCode !== 0) {
      // Include complete stderr logs in error message (no truncation)
      // Combine stderr and stdout for complete error context
      const completeErrorLogs = stderr.trim() || stdoutTrimmed || `Python exited with code ${exitCode}`;
      await prisma.submissionLog.update({
        where: { id: submission.id },
        data: {
          status: "failed",
          message: completeErrorLogs,
          finishedAt: new Date(),
        },
      });
      
      // Error status already updated in database - no need to return here
    }

    // Exit code is 0 but no JSON found - try to parse whole stdout as JSON, otherwise treat as success with message
    try {
      parsed = JSON.parse(stdoutTrimmed || "{}");
      if (parsed && typeof parsed === "object") {
      // Include complete logs (stderr + stdout) for successful submissions
      const completeLogs = (stderr.trim() || stdoutTrimmed || parsed.message || "").trim();
      await prisma.submissionLog.update({
        where: { id: submission.id },
        data: {
          status: parsed.status === "success" ? "success" : parsed.status ?? "success",
          message: completeLogs || null,
          finishedAt: new Date(),
        },
      });
      // Status already updated in database - no need to return here
      }
    } catch (parseError) {
      // Not JSON, treat as success with complete message output
      const completeLogs = (stderr.trim() || stdoutTrimmed || "Automation complete.").trim();
      await prisma.submissionLog.update({
        where: { id: submission.id },
        data: {
          status: "success",
          message: completeLogs,
          finishedAt: new Date(),
        },
      });
      // Status already updated in database - no need to return here
    }
      } catch (processError) {
        // Handle errors in background process
        const errorMessage = (processError as Error).message || "Unknown error";
        await prisma.submissionLog.update({
          where: { id: submission.id },
          data: {
            status: "failed",
            message: errorMessage,
            finishedAt: new Date(),
          },
        }).catch(() => undefined);
        await rm(tempDir, { recursive: true, force: true }).catch(() => undefined);
      }
    })(); // End of async IIFE - runs in background

    // Return immediately with submission ID - don't wait for automation
    return NextResponse.json(
      { 
        status: "running", 
        message: "Automation started", 
        submissionId: submission.id 
      },
      { status: 202 } // 202 Accepted - request accepted but not yet completed
    );
  } catch (error) {
    return NextResponse.json(
      { status: "error", message: (error as Error).message },
      { status: 500 }
    );
  }
}


