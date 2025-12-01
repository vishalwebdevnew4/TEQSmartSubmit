import { NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";
import { prisma } from "@/lib/prisma";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const { businessId, templateVersionId, githubRepoUrl } = await request.json();

    if (!businessId || !templateVersionId) {
      return NextResponse.json(
        { success: false, error: "Missing businessId or templateVersionId" },
        { status: 400 }
      );
    }

    // Fetch template version to get temp directory
    const templateVersion = await prisma.templateVersion.findUnique({
      where: { id: parseInt(templateVersionId) },
      include: { template: true },
    });

    if (!templateVersion) {
      return NextResponse.json(
        { success: false, error: "Template version not found" },
        { status: 404 }
      );
    }

    // Create deployment log
    const deploymentLog = await prisma.deploymentLog.create({
      data: {
        businessId: parseInt(businessId),
        templateVersionId: parseInt(templateVersionId),
        status: "deploying",
      },
    });

    // Call Python deployment service
    const scriptPath = path.join(process.cwd(), "backend", "app", "services", "vercel_deploy.py");
    
    // Get temp directory from template version content (stored in previous step)
    // For now, we'll need to pass it or store it differently
    const tempDir = (templateVersion.content as any)?._tempDir || "/tmp/website";

    const pythonProcess = spawn(
      "python",
      [
        scriptPath,
        "--template-path",
        tempDir,
        ...(githubRepoUrl ? ["--github-repo", githubRepoUrl] : []),
      ],
      {
        cwd: process.cwd(),
        stdio: ["pipe", "pipe", "pipe"],
      }
    );

    let stdout = "";
    let stderr = "";

    pythonProcess.stdout.on("data", (data) => {
      stdout += data.toString();
    });

    pythonProcess.stderr.on("data", (data) => {
      stderr += data.toString();
    });

    const result = await new Promise<{ success: boolean; data?: any; error?: string }>((resolve) => {
      pythonProcess.on("close", (code) => {
        if (code === 0) {
          try {
            const data = JSON.parse(stdout);
            resolve({ success: true, data });
          } catch (e) {
            resolve({ success: false, error: "Failed to parse response" });
          }
        } else {
          resolve({ success: false, error: stderr || "Python script failed" });
        }
      });
    });

    // Update deployment log
    if (result.success && result.data) {
      await prisma.deploymentLog.update({
        where: { id: deploymentLog.id },
        data: {
          status: result.data.vercel_deployed ? "success" : "failed",
          vercelUrl: result.data.vercel_url || null,
          githubRepoUrl: result.data.github_repo_url || githubRepoUrl || null,
          deployedAt: new Date(),
          errorMessage: result.data.errors?.length ? result.data.errors.join(", ") : null,
        },
      });

      // Take screenshot if deployment successful
      if (result.data.vercel_url) {
        // Trigger screenshot in background
        fetch("/api/businesses/screenshot", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            url: result.data.vercel_url,
            deploymentId: deploymentLog.id,
          }),
        }).catch(console.error);
      }
    } else {
      await prisma.deploymentLog.update({
        where: { id: deploymentLog.id },
        data: {
          status: "failed",
          errorMessage: result.error || "Deployment failed",
        },
      });
    }

    return NextResponse.json({
      success: result.success,
      deployment: await prisma.deploymentLog.findUnique({
        where: { id: deploymentLog.id },
        include: { business: true },
      }),
      errors: result.data?.errors || [],
    });
  } catch (error: any) {
    console.error("Error deploying website:", error);
    return NextResponse.json(
      { success: false, error: error.message || "Failed to deploy website" },
      { status: 500 }
    );
  }
}

