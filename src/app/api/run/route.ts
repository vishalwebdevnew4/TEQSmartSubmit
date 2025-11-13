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

    const tempDir = await mkdtemp(path.join(os.tmpdir(), "teq-template-"));
    const templatePath = path.join(tempDir, "template.json");
    await writeFile(templatePath, JSON.stringify(template, null, 2), "utf8");

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

    const exitCode: number = await new Promise((resolve, reject) => {
      python.on("error", reject);
      python.on("close", resolve);
    });

    await rm(tempDir, { recursive: true, force: true }).catch(() => undefined);

    if (exitCode !== 0) {
      await prisma.submissionLog.update({
        where: { id: submission.id },
        data: {
          status: "failed",
          message: stderr.trim() || stdout.trim() || `Python exited with code ${exitCode}`,
          finishedAt: new Date(),
        },
      });
      return NextResponse.json(
        {
          status: "error",
          message: stderr.trim() || stdout.trim() || `Python exited with code ${exitCode}`,
        },
        { status: 500 }
      );
    }

    try {
      const parsed = JSON.parse(stdout || "{}");
      await prisma.submissionLog.update({
        where: { id: submission.id },
        data: {
          status: parsed.status === "success" ? "success" : parsed.status ?? "success",
          message: parsed.message ?? null,
          finishedAt: new Date(),
        },
      });
      return NextResponse.json({ ...parsed, submissionId: submission.id });
    } catch (parseError) {
      const message = stdout.trim() || "Automation complete.";
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


