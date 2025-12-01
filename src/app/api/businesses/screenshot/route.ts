import { NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";
import { prisma } from "@/lib/prisma";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const { url, deploymentId } = await request.json();

    if (!url) {
      return NextResponse.json(
        { success: false, error: "Missing URL" },
        { status: 400 }
      );
    }

    // Call Python screenshot service
    const scriptPath = path.join(process.cwd(), "backend", "app", "services", "screenshot_service.py");
    const outputPath = `/tmp/screenshots/deployment-${deploymentId || Date.now()}.png`;

    const pythonProcess = spawn(
      "python",
      [scriptPath, "--url", url, "--output", outputPath, "--full-page"],
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

    if (result.success && result.data?.screenshot_path && deploymentId) {
      // Update deployment log with screenshot URL
      // In production, upload screenshot to S3/Cloudinary and use that URL
      await prisma.deploymentLog.update({
        where: { id: parseInt(deploymentId) },
        data: {
          screenshotUrl: result.data.screenshot_path, // Or uploaded URL
        },
      });
    }

    return NextResponse.json({
      success: result.success,
      screenshotPath: result.data?.screenshot_path,
      error: result.error,
    });
  } catch (error: any) {
    console.error("Error taking screenshot:", error);
    return NextResponse.json(
      { success: false, error: error.message || "Failed to take screenshot" },
      { status: 500 }
    );
  }
}

