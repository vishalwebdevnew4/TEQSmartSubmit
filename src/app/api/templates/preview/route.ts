import { NextResponse } from "next/server";
import fs from "fs/promises";
import path from "path";

export const dynamic = "force-dynamic";

/**
 * GET /api/templates/preview?category=restaurant&name=restaurant-template-1
 * Serves the template HTML file for preview
 */
export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const category = searchParams.get("category");
    const templateName = searchParams.get("name");

    if (!category || !templateName) {
      return NextResponse.json(
        { error: "Missing category or name parameter" },
        { status: 400 }
      );
    }

    const templatePath = path.join(
      process.cwd(),
      "templates",
      category,
      templateName,
      "index.html"
    );

    try {
      const html = await fs.readFile(templatePath, "utf-8");
      
      // Inject base path for assets - handle both relative and absolute paths
      const basePath = `/api/templates/assets?category=${encodeURIComponent(category)}&name=${encodeURIComponent(templateName)}&file=`;
      const templateBaseDir = path.join(process.cwd(), "templates", category, templateName);
      
      const modifiedHtml = html.replace(
        /(href|src)=["']([^"']+)["']/g,
        (match, attr, url) => {
          // Skip external URLs
          if (url.startsWith("http://") || url.startsWith("https://") || url.startsWith("//") || url.startsWith("data:")) {
            return match;
          }
          
          // Handle relative paths
          let cleanUrl = url.replace(/^\.\//, "").replace(/^\//, "");
          // Ensure we're serving from the template directory
          return `${attr}="${basePath}${cleanUrl}"`;
        }
      );

      return new NextResponse(modifiedHtml, {
        headers: {
          "Content-Type": "text/html; charset=utf-8",
          "Cache-Control": "no-cache, no-store, must-revalidate",
          "X-Content-Type-Options": "nosniff",
        },
      });
    } catch (error: any) {
      if (error.code === "ENOENT") {
        return NextResponse.json(
          { error: "Template not found" },
          { status: 404 }
        );
      }
      throw error;
    }
  } catch (error: any) {
    console.error("Error serving template preview:", error);
    return NextResponse.json(
      { error: error.message || "Failed to serve template" },
      { status: 500 }
    );
  }
}

