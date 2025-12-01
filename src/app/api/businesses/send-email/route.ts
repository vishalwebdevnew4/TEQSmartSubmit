import { NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";
import { prisma } from "@/lib/prisma";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const { clientId, businessId, previewUrl, screenshotUrl, message } = await request.json();

    if (!clientId || !businessId || !previewUrl) {
      return NextResponse.json(
        { success: false, error: "Missing required fields" },
        { status: 400 }
      );
    }

    // Fetch client and business
    const client = await prisma.client.findUnique({
      where: { id: parseInt(clientId) },
      include: { business: true },
    });

    if (!client) {
      return NextResponse.json(
        { success: false, error: "Client not found" },
        { status: 404 }
      );
    }

    const business = client.business;

    // Call Python email service
    const scriptPath = path.join(process.cwd(), "backend", "app", "services", "email_service.py");

    const pythonProcess = spawn(
      "python",
      [
        scriptPath,
        "--to",
        client.email,
        "--business-name",
        business.name,
        "--preview-url",
        previewUrl,
        ...(screenshotUrl ? ["--screenshot-url", screenshotUrl] : []),
        ...(message ? ["--message", message] : []),
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

    if (result.success) {
      // Update client status
      await prisma.client.update({
        where: { id: parseInt(clientId) },
        data: {
          status: "sent",
          emailSentAt: new Date(),
          previewUrl,
          screenshotUrl: screenshotUrl || null,
          message: message || null,
        },
      });

      // Create tracking event
      await prisma.clientTracking.create({
        data: {
          clientId: parseInt(clientId),
          eventType: "email_sent",
        },
      });
    }

    return NextResponse.json({
      success: result.success,
      error: result.error,
    });
  } catch (error: any) {
    console.error("Error sending email:", error);
    return NextResponse.json(
      { success: false, error: error.message || "Failed to send email" },
      { status: 500 }
    );
  }
}

