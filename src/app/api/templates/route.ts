import { NextResponse } from "next/server";
import fs from "fs/promises";
import path from "path";

export const dynamic = "force-dynamic";

/**
 * GET /api/templates
 * Returns all downloaded templates organized by category
 */
export async function GET() {
  try {
    const templatesDir = path.join(process.cwd(), "templates");
    
    // Check if templates directory exists
    try {
      await fs.access(templatesDir);
    } catch {
      return NextResponse.json({ templates: [], total: 0, byCategory: {} });
    }

    const categories = await fs.readdir(templatesDir);
    const templates: any[] = [];
    const byCategory: Record<string, any[]> = {};

    for (const category of categories) {
      const categoryPath = path.join(templatesDir, category);
      const stat = await fs.stat(categoryPath);
      
      if (!stat.isDirectory()) continue;

      const templateDirs = await fs.readdir(categoryPath);
      byCategory[category] = [];

      for (const templateName of templateDirs) {
        const templatePath = path.join(categoryPath, templateName);
        const templateStat = await fs.stat(templatePath);
        
        if (!templateStat.isDirectory()) continue;

        // Read metadata.json if it exists
        const metadataPath = path.join(templatePath, "metadata.json");
        let metadata: any = {
          name: templateName,
          category: category,
          status: "downloaded",
        };

        try {
          const metadataContent = await fs.readFile(metadataPath, "utf-8");
          metadata = { ...metadata, ...JSON.parse(metadataContent) };
        } catch {
          // Metadata file doesn't exist, use defaults
        }

        // Check if index.html exists
        const indexPath = path.join(templatePath, "index.html");
        let hasPreview = false;
        try {
          await fs.access(indexPath);
          hasPreview = true;
        } catch {
          hasPreview = false;
        }

        const template = {
          ...metadata,
          path: `/templates/${category}/${templateName}`,
          previewUrl: hasPreview ? `/api/templates/preview?category=${category}&name=${templateName}` : null,
          localPath: templatePath,
        };

        templates.push(template);
        byCategory[category].push(template);
      }
    }

    return NextResponse.json({
      templates,
      total: templates.length,
      byCategory,
      categories: Object.keys(byCategory),
    });
  } catch (error: any) {
    console.error("Error fetching templates:", error);
    return NextResponse.json(
      { error: error.message || "Failed to fetch templates" },
      { status: 500 }
    );
  }
}
