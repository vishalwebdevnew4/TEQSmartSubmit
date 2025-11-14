import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { urls, category, isActive } = body;

    if (!Array.isArray(urls) || urls.length === 0) {
      return NextResponse.json({ detail: "URLs array is required." }, { status: 400 });
    }

    const results = {
      created: 0,
      skipped: 0,
      errors: [] as string[],
    };

    for (const url of urls) {
      if (!url || typeof url !== "string") {
        results.skipped++;
        results.errors.push(`Invalid URL: ${url}`);
        continue;
      }

      // Validate URL format
      try {
        new URL(url);
      } catch {
        results.skipped++;
        results.errors.push(`Invalid URL format: ${url}`);
        continue;
      }

      try {
        await prisma.domain.create({
          data: {
            url: url.trim(),
            category: category || null,
            isActive: isActive !== undefined ? isActive : true,
          },
        });
        results.created++;
      } catch (error: any) {
        if (error.code === "P2002") {
          results.skipped++;
          results.errors.push(`Domain already exists: ${url}`);
        } else {
          results.skipped++;
          results.errors.push(`Error creating domain ${url}: ${(error as Error).message}`);
        }
      }
    }

    return NextResponse.json({
      message: `Processed ${urls.length} URLs. Created: ${results.created}, Skipped: ${results.skipped}`,
      ...results,
    });
  } catch (error) {
    return NextResponse.json(
      { detail: (error as Error).message ?? "Unable to upload domains." },
      { status: 500 }
    );
  }
}

