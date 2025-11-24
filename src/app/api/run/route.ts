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
    
    // If template explicitly sets headless, use that; otherwise default to non-headless
    // For sites with CAPTCHA (especially audio challenges), prefer visible browser (headless=false)
    const templateHeadless = template.headless ?? template.Headless;
    let shouldUseHeadless: boolean;
    
    if (templateHeadless !== undefined) {
      // Template explicitly sets headless mode
      shouldUseHeadless = templateHeadless;
    } else if (forceHeadless) {
      // Environment forces headless
      shouldUseHeadless = true;
    } else {
      // Default to non-headless for better CAPTCHA solving (especially audio challenges)
      // Test mode and normal mode both use visible browser by default
      shouldUseHeadless = false;
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

    // Use the correct script - form_discovery.py is the main automation script
    const scriptPath = path.join(process.cwd(), "automation", "submission", "form_discovery.py");
    
    // Verify script exists
    const fs = require('fs');
    if (!fs.existsSync(scriptPath)) {
      return NextResponse.json(
        { 
          status: "error", 
          message: `Python script not found at: ${scriptPath}. Please verify the file exists.` 
        },
        { status: 500 }
      );
    }
    
    // Log the script path being used
    console.log(`[AUTOMATION] Using script path: ${scriptPath}`);
    console.log(`[AUTOMATION] Script exists: ${fs.existsSync(scriptPath)}`);

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
        
        // Check if xvfb-run is available (doesn't require sudo, just needs to be installed)
        // This allows visible browser mode on headless servers without Xvfb installation
        let useXvfbRun = false;
        if (os.platform() !== "win32" && !process.env.DISPLAY) {
          try {
            const { execSync } = require('child_process');
            execSync('which xvfb-run', { stdio: 'ignore', timeout: 2000 });
            useXvfbRun = true;
            console.log('[AUTOMATION] xvfb-run detected - will use for virtual display');
          } catch {
            // xvfb-run not available, will try other methods
            console.log('[AUTOMATION] xvfb-run not available - will try other display methods');
          }
        }
    
    // Return immediately with submission ID - let automation run in background
    // This prevents the API from timing out while automation is running
    (async () => {
      try {
        // Verify script exists
        const fs = require('fs');
        if (!fs.existsSync(scriptPath)) {
          const errorMsg = `❌ CRITICAL ERROR: Python script not found!\n` +
            `Expected path: ${scriptPath}\n` +
            `Current working directory: ${process.cwd()}\n` +
            `Please verify the script exists at the correct location.`;
          
          await prisma.submissionLog.update({
            where: { id: submission.id },
            data: {
              status: "failed",
              message: errorMsg,
              finishedAt: new Date(),
            },
          });
          return; // Exit early
        }

        // Log that we're starting the process with full details
        const startupMessage = `🚀 Starting Python automation script...\n\n` +
          `Script Path: ${scriptPath}\n` +
          `Script Exists: ✅ Yes\n` +
          `Python Command: ${pythonCommand}\n` +
          `Target URL: ${url}\n` +
          `Template Path: ${templatePath}\n` +
          `Working Directory: ${process.cwd()}\n` +
          `Timestamp: ${new Date().toISOString()}\n\n` +
          `Waiting for Python process to start and produce output...`;
        
        await prisma.submissionLog.update({
          where: { id: submission.id },
          data: {
            message: startupMessage,
          },
        });

        // Build command - use xvfb-run wrapper if available and no DISPLAY is set
        let finalCommand = pythonCommand;
        let finalArgs = [scriptPath, "--url", url, "--template", templatePath];
        
        if (useXvfbRun) {
          finalCommand = "xvfb-run";
          finalArgs = [
            "-a", // Auto-display-number
            "-s", "-screen 0 1280x720x24", // Screen settings
            pythonCommand,
            ...finalArgs
          ];
          console.log('[AUTOMATION] Using xvfb-run wrapper for virtual display');
        }
        
        const python = spawn(finalCommand, finalArgs, {
          cwd: process.cwd(),
          env: { 
            ...process.env, 
            PYTHONUNBUFFERED: "1", 
            PYTHONIOENCODING: "utf-8",
            // Force immediate output
            PYTHON_FLUSH: "1"
          },
          // Ensure we can capture output immediately
          stdio: ['ignore', 'pipe', 'pipe']
        });

        python.stdout.setEncoding("utf8");
        python.stderr.setEncoding("utf8");
        
        // Set streams to flowing mode for immediate output
        python.stdout.resume();
        python.stderr.resume();

        let stdout = "";
        let stderr = "";
        let lastLogUpdate = Date.now();
        const LOG_UPDATE_INTERVAL = 1000; // Update database every 1 second with logs (more frequent)
        let processStartTime = Date.now();
        let hasReceivedAnyOutput = false;

        // Handle stdout
        python.stdout.on("data", async (chunk) => {
          stdout += chunk;
          hasReceivedAnyOutput = true;
        });

        // Handle stderr - update database immediately for EVERY chunk (no delay)
        python.stderr.on("data", async (chunk) => {
          stderr += chunk;
          hasReceivedAnyOutput = true;
          
          // Update database immediately for EVERY chunk
          try {
            await prisma.submissionLog.update({
              where: { id: submission.id },
              data: {
                message: stderr || "Automation in progress...",
              },
            });
            lastLogUpdate = Date.now();
          } catch (updateError) {
            // Ignore update errors to avoid breaking the main flow
            console.error("Failed to update log:", updateError);
          }
        });

        // Handle process errors (script not found, permission denied, etc.)
        python.on("error", async (error) => {
          const err = error as NodeJS.ErrnoException;
          const errorMsg = `❌ CRITICAL ERROR: Failed to start Python process!\n\n` +
            `Error: ${error.message}\n` +
            `Error Code: ${err.code || 'N/A'}\n` +
            `Command: ${pythonCommand} ${scriptPath} --url ${url} --template ${templatePath}\n\n` +
            `Possible causes:\n` +
            `1. Python not installed or not in PATH\n` +
            `2. Script file permissions issue\n` +
            `3. Script path is incorrect\n` +
            `4. Missing dependencies\n\n` +
            `Please check server logs for more details.`;
          
          await prisma.submissionLog.update({
            where: { id: submission.id },
            data: {
              status: "failed",
              message: errorMsg,
              finishedAt: new Date(),
            },
          });
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
          python.on("close", async (code) => {
            clearTimeout(timeoutId);
            const duration = Date.now() - processStartTime;
            
            // If process completed too quickly (< 5 seconds) and we got no output, it likely failed
            if (duration < 5000 && !hasReceivedAnyOutput && (stdout.trim().length === 0 && stderr.trim().length === 0)) {
              const errorMsg = `❌ CRITICAL ERROR: Process exited too quickly with NO output!\n\n` +
                `Duration: ${duration}ms (expected: 30+ seconds)\n` +
                `Exit Code: ${code}\n` +
                `Script Path: ${scriptPath}\n` +
                `Python Command: ${pythonCommand}\n` +
                `URL: ${url}\n\n` +
                `This usually means:\n` +
                `1. ❌ Python script has a syntax error or import error\n` +
                `2. ❌ Script path is incorrect\n` +
                `3. ❌ Python command not found or wrong version\n` +
                `4. ❌ Script exited immediately without running\n` +
                `5. ❌ Missing required dependencies (playwright, etc.)\n\n` +
                `STDOUT captured: ${stdout.length > 0 ? stdout.substring(0, 500) : '(empty)'}\n` +
                `STDERR captured: ${stderr.length > 0 ? stderr.substring(0, 500) : '(empty)'}\n\n` +
                `Please check:\n` +
                `- Run manually: ${pythonCommand} ${scriptPath} --url "${url}" --template "${templatePath}"\n` +
                `- Check server console logs for Python errors\n` +
                `- Verify Python and dependencies are installed`;
              
              await prisma.submissionLog.update({
                where: { id: submission.id },
                data: {
                  status: "failed",
                  message: errorMsg,
                  finishedAt: new Date(),
                },
              });
            } else if (duration < 5000 && (stdout.trim().length > 0 || stderr.trim().length > 0)) {
              // Got some output but still too fast - log what we got
              const partialMsg = `⚠️  Process completed very quickly (${duration}ms) but got some output:\n\n` +
                `STDOUT (first 1000 chars):\n${stdout.substring(0, 1000)}\n\n` +
                `STDERR (first 1000 chars):\n${stderr.substring(0, 1000)}`;
              
              await prisma.submissionLog.update({
                where: { id: submission.id },
                data: {
                  message: partialMsg,
                },
              });
            }
            
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
      
      // Build complete logs: prioritize parsed.message, then combine with stderr
      let completeLogs = "";
      
      // First, get the detailed message from parsed result
      if (parsed.message && parsed.message.trim().length > 0) {
        completeLogs = parsed.message.trim();
      }
      
      // Add stderr logs if they exist and aren't already in the message
      if (stderr.trim().length > 0) {
        if (completeLogs && !completeLogs.includes(stderr.trim().substring(0, 100))) {
          // Append stderr if it's not already included
          completeLogs += "\n\n" + "=".repeat(80) + "\n";
          completeLogs += "REAL-TIME LOGS FROM STDERR\n";
          completeLogs += "=".repeat(80) + "\n";
          completeLogs += stderr.trim();
        } else if (!completeLogs) {
          completeLogs = stderr.trim();
        }
      }
      
      // Fallback if still empty
      if (!completeLogs || completeLogs.trim().length === 0) {
        completeLogs = stdoutTrimmed || "No logs available - process may have completed too quickly";
      }
      
      const finalMessage = completeLogs.trim();
      
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
      // Prioritize parsed.message which contains detailed execution logs
      const completeLogs = (parsed.message || stderr.trim() || stdoutTrimmed || "").trim();
      await prisma.submissionLog.update({
        where: { id: submission.id },
        data: {
          status: parsed.status === "success" ? "success" : parsed.status ?? "success",
          message: completeLogs || "No logs available",
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


