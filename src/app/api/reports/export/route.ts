import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const type = searchParams.get("type") || "all";
    const format = searchParams.get("format") || "json";

    let data: any = {};

    if (type === "all" || type === "businesses") {
      data.businesses = await prisma.business.findMany({
        include: {
          deployments: true,
          clients: true,
          formSubmissions: true,
        },
      });
    }

    if (type === "all" || type === "deployments") {
      data.deployments = await prisma.deploymentLog.findMany({
        include: {
          business: true,
          templateVersion: true,
        },
      });
    }

    if (type === "all" || type === "clients") {
      data.clients = await prisma.client.findMany({
        include: {
          business: true,
          tracking: true,
        },
      });
    }

    if (type === "all" || type === "submissions") {
      data.submissions = await prisma.formSubmissionLog.findMany({
        include: {
          business: true,
        },
      });
    }

    if (format === "csv") {
      // Convert to CSV
      const csv = convertToCSV(data);
      return new NextResponse(csv, {
        headers: {
          "Content-Type": "text/csv",
          "Content-Disposition": `attachment; filename="report-${Date.now()}.csv"`,
        },
      });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error("Error exporting report:", error);
    return NextResponse.json(
      { error: "Failed to export report" },
      { status: 500 }
    );
  }
}

function convertToCSV(data: any): string {
  // Simple CSV conversion
  const lines: string[] = [];
  
  for (const [key, value] of Object.entries(data)) {
    if (Array.isArray(value) && value.length > 0) {
      lines.push(`\n=== ${key.toUpperCase()} ===\n`);
      const headers = Object.keys(value[0]).join(",");
      lines.push(headers);
      
      for (const item of value) {
        const row = Object.values(item)
          .map((v) => {
            if (v === null || v === undefined) return "";
            if (typeof v === "object") return JSON.stringify(v);
            return String(v).replace(/,/g, ";");
          })
          .join(",");
        lines.push(row);
      }
    }
  }
  
  return lines.join("\n");
}
