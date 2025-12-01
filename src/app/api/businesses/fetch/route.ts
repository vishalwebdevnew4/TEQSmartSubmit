import { NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";
import { prisma } from "@/lib/prisma";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const { input, inputType } = await request.json();

    if (!input || !inputType) {
      return NextResponse.json(
        { success: false, error: "Missing input or inputType" },
        { status: 400 }
      );
    }

    // Call Python service to fetch Google Places data
    const scriptPath = path.join(process.cwd(), "backend", "app", "services", "google_places_service.py");
    
    const pythonProcess = spawn("python", [scriptPath, "--input", input, "--type", inputType], {
      cwd: process.cwd(),
      stdio: ["pipe", "pipe", "pipe"],
    });

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

    if (!result.success) {
      return NextResponse.json(
        { success: false, error: result.error },
        { status: 500 }
      );
    }

    // Save to database
    const business = await prisma.business.create({
      data: {
        name: result.data.name,
        phone: result.data.phone,
        address: result.data.address,
        website: result.data.website,
        googlePlacesUrl: result.data.googlePlacesUrl,
        googlePlacesId: result.data.googlePlacesId,
        description: result.data.description,
        categories: result.data.categories,
        reviews: result.data.reviews,
        images: result.data.images,
        rating: result.data.rating,
        reviewCount: result.data.reviewCount,
        rawData: result.data.rawData,
      },
    });

    return NextResponse.json({ success: true, business });
  } catch (error: any) {
    console.error("Error fetching business:", error);
    return NextResponse.json(
      { success: false, error: error.message || "Failed to fetch business" },
      { status: 500 }
    );
  }
}

