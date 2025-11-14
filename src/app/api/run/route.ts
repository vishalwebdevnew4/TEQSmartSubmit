import { NextRequest, NextResponse } from "next/server";
import { spawn } from "node:child_process";
import { mkdtemp, writeFile, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";

import { prisma } from "@/lib/prisma";

export const runtime = "nodejs";

export async function POST(req: NextRequest) {
  try {
    const { url, template, domainId, templateId, adminId } = await req.json();

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

    // Ensure local CAPTCHA solver is enabled by default if not explicitly set
    // This prevents falling back to external services with invalid API keys
    const enhancedTemplate = {
      ...template,
      use_local_captcha_solver: template.use_local_captcha_solver ?? true,
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

    const python = spawn("python3", [scriptPath, "--url", url, "--template", templatePath], {
      cwd: process.cwd(),
      env: { ...process.env, PYTHONUNBUFFERED: "1" },
    });

    python.stdout.setEncoding("utf8");
    python.stderr.setEncoding("utf8");

    let stdout = "";
    let stderr = "";

    python.stdout.on("data", (chunk) => {
      stdout += chunk;
    });

    python.stderr.on("data", (chunk) => {
      stderr += chunk;
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
      const finalMessage = parsed.message || stdoutTrimmed || null;
      
      await prisma.submissionLog.update({
        where: { id: submission.id },
        data: {
          status: finalStatus,
          message: finalMessage,
          finishedAt: new Date(),
        },
      });
      
      // Return appropriate status code based on automation result
      if (finalStatus === "success") {
        return NextResponse.json(
          { ...parsed, submissionId: submission.id, status: finalStatus },
          { status: 200 }
        );
      } else {
        return NextResponse.json(
          { ...parsed, submissionId: submission.id, status: finalStatus },
          { status: 500 }
        );
      }
    }

    // If exit code is non-zero and no JSON found, treat as error
    if (exitCode !== 0) {
      const errorMessage = stderr.trim() || stdoutTrimmed || `Python exited with code ${exitCode}`;
      await prisma.submissionLog.update({
        where: { id: submission.id },
        data: {
          status: "failed",
          message: errorMessage,
          finishedAt: new Date(),
        },
      });
      
      // Check if it was a timeout
      if (errorMessage.includes("SIGTERM") || errorMessage.includes("killed")) {
        return NextResponse.json(
          {
            status: "error",
            message: "Automation timed out after 5 minutes. The script may still be running in the background.",
          },
          { status: 500 }
        );
      }
      
      return NextResponse.json(
        {
          status: "error",
          message: errorMessage,
          submissionId: submission.id,
        },
        { status: 500 }
      );
    }

    // Exit code is 0 but no JSON found - try to parse whole stdout as JSON, otherwise treat as success with message
    try {
      parsed = JSON.parse(stdoutTrimmed || "{}");
      if (parsed && typeof parsed === "object") {
        await prisma.submissionLog.update({
          where: { id: submission.id },
          data: {
            status: parsed.status === "success" ? "success" : parsed.status ?? "success",
            message: parsed.message ?? null,
            finishedAt: new Date(),
          },
        });
        return NextResponse.json({ ...parsed, submissionId: submission.id });
      }
    } catch (parseError) {
      // Not JSON, treat as success with message output
      const message = stdoutTrimmed || "Automation complete.";
      await prisma.submissionLog.update({
        where: { id: submission.id },
        data: {
          status: "success",
          message,
          finishedAt: new Date(),
        },
      });
      return NextResponse.json(
        { status: "success", message, submissionId: submission.id },
        { status: 200 }
      );
    }
  } catch (error) {
    return NextResponse.json(
      { status: "error", message: (error as Error).message },
      { status: 500 }
    );
  }
}


