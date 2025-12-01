import { NextResponse } from "next/server";
import { readdir } from "fs/promises";
import { join } from "path";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const appDir = join(process.cwd(), "src", "app");
    
    // Get all page.tsx files
    const pages: string[] = [];
    
    async function findPages(dir: string, basePath: string = "") {
      try {
        const entries = await readdir(dir, { withFileTypes: true });
        
        for (const entry of entries) {
          const fullPath = join(dir, entry.name);
          const routePath = basePath ? `${basePath}/${entry.name}` : entry.name;
          
          if (entry.isDirectory()) {
            // Skip route groups and special directories
            if (!entry.name.startsWith("(") && entry.name !== "api" && entry.name !== "fonts") {
              await findPages(fullPath, routePath);
            }
          } else if (entry.name === "page.tsx") {
            pages.push(basePath || "/");
          }
        }
      } catch (error) {
        // Ignore errors
      }
    }
    
    await findPages(appDir);
    
    return NextResponse.json({
      routes: pages.sort(),
      total: pages.length,
      message: "Available routes",
    });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message, routes: [] },
      { status: 500 }
    );
  }
}

