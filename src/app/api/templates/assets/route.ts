import { NextResponse } from "next/server";
import fs from "fs/promises";
import path from "path";

export const dynamic = "force-dynamic";

/**
 * GET /api/templates/assets?category=restaurant&name=restaurant-template-1&file=assets/css/style.css
 * Serves template assets (CSS, JS, images)
 */
export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const category = searchParams.get("category");
    const templateName = searchParams.get("name");
    const file = searchParams.get("file");

    if (!category || !templateName || !file) {
      return NextResponse.json(
        { error: "Missing required parameters" },
        { status: 400 }
      );
    }

    // Security: prevent directory traversal
    if (file.includes("..") || file.startsWith("/")) {
      return NextResponse.json(
        { error: "Invalid file path" },
        { status: 400 }
      );
    }

    const filePath = path.join(
      process.cwd(),
      "templates",
      category,
      templateName,
      file
    );

    try {
      const fileContent = await fs.readFile(filePath);
      const ext = path.extname(file).toLowerCase();
      
      const contentType: Record<string, string> = {
        ".css": "text/css",
        ".js": "application/javascript",
        ".json": "application/json",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".webp": "image/webp",
        ".woff": "font/woff",
        ".woff2": "font/woff2",
        ".ttf": "font/ttf",
        ".eot": "application/vnd.ms-fontobject",
      };

      return new NextResponse(fileContent, {
        headers: {
          "Content-Type": contentType[ext] || "application/octet-stream",
        },
      });
    } catch (error: any) {
      if (error.code === "ENOENT") {
        return NextResponse.json(
          { error: "Asset not found" },
          { status: 404 }
        );
      }
      throw error;
    }
  } catch (error: any) {
    console.error("Error serving template asset:", error);
    return NextResponse.json(
      { error: error.message || "Failed to serve asset" },
      { status: 500 }
    );
  }
}

