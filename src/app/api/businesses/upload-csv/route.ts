import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { parse } from "csv-parse/sync";
import { Readable } from "stream";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const file = formData.get("file") as File;

    if (!file) {
      return NextResponse.json(
        { success: false, error: "No file provided" },
        { status: 400 }
      );
    }

    // Read file content
    const buffer = Buffer.from(await file.arrayBuffer());
    const content = buffer.toString("utf-8");

    // Parse CSV
    const records = parse(content, {
      columns: true,
      skip_empty_lines: true,
      trim: true,
    });

    if (!records || records.length === 0) {
      return NextResponse.json(
        { success: false, error: "CSV file is empty or invalid" },
        { status: 400 }
      );
    }

    // Process each row
    const results = [];
    const errors = [];

    for (const row of records) {
      try {
        // Try to find business by name, phone, or URL
        const name = row.name || row.business_name || row["Business Name"];
        const phone = row.phone || row.phone_number || row["Phone Number"];
        const url = row.url || row.google_places_url || row["Google Places URL"];

        if (!name && !phone && !url) {
          errors.push({ row, error: "Missing name, phone, or URL" });
          continue;
        }

        // Check if business already exists
        const existing = await prisma.business.findFirst({
          where: {
            OR: [
              name ? { name } : {},
              phone ? { phone } : {},
              url ? { googlePlacesUrl: url } : {},
            ],
          },
        });

        if (existing) {
          results.push({ business: existing, created: false });
          continue;
        }

        // Create business record (without Google Places data for now)
        // User can fetch full data later using the fetch endpoint
        const business = await prisma.business.create({
          data: {
            name: name || "Unknown Business",
            phone: phone || null,
            website: url || null,
            googlePlacesUrl: url || null,
          },
        });

        results.push({ business, created: true });
      } catch (error: any) {
        errors.push({ row, error: error.message });
      }
    }

    return NextResponse.json({
      success: true,
      created: results.filter((r) => r.created).length,
      existing: results.filter((r) => !r.created).length,
      errors: errors.length,
      results,
      errors: errors.length > 0 ? errors : undefined,
    });
  } catch (error: any) {
    console.error("Error uploading CSV:", error);
    return NextResponse.json(
      { success: false, error: error.message || "Failed to upload CSV" },
      { status: 500 }
    );
  }
}

