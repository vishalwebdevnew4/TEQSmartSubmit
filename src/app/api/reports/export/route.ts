import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const format = searchParams.get("format") || "csv";
    const status = searchParams.get("status");
    const startDate = searchParams.get("startDate");
    const endDate = searchParams.get("endDate");
    const domainId = searchParams.get("domainId");

    const where: any = {};
    if (status) where.status = status;
    if (domainId) where.domainId = parseInt(domainId);
    if (startDate || endDate) {
      where.createdAt = {};
      if (startDate) {
        const start = new Date(startDate);
        // If it's just a date string (YYYY-MM-DD), set to start of day
        if (startDate.split("T").length === 1) {
          start.setHours(0, 0, 0, 0);
        }
        where.createdAt.gte = start;
      }
      if (endDate) {
        const end = new Date(endDate);
        // If it's just a date string (YYYY-MM-DD), set to end of day
        if (endDate.split("T").length === 1) {
          end.setHours(23, 59, 59, 999);
        }
        where.createdAt.lte = end;
      }
    }

    const logs = await prisma.submissionLog.findMany({
      where,
      include: {
        domain: {
          select: {
            url: true,
          },
        },
        template: {
          select: {
            name: true,
          },
        },
      },
      orderBy: {
        createdAt: "desc",
      },
    });

    if (format === "csv") {
      const csvHeaders = "ID,URL,Domain,Template,Status,Message,Created At,Finished At\n";
      const csvRows = logs.map((log) => {
        const escape = (str: string | null | undefined) => {
          if (!str) return "";
          return `"${String(str).replace(/"/g, '""')}"`;
        };
        return [
          log.id,
          escape(log.url),
          escape(log.domain?.url || ""),
          escape(log.template?.name || ""),
          escape(log.status),
          escape(log.message || ""),
          escape(log.createdAt.toISOString()),
          escape(log.finishedAt?.toISOString() || ""),
        ].join(",");
      });
      const csv = csvHeaders + csvRows.join("\n");

      return new NextResponse(csv, {
        headers: {
          "Content-Type": "text/csv",
          "Content-Disposition": `attachment; filename="submission-logs-${new Date().toISOString().split("T")[0]}.csv"`,
        },
      });
    } else if (format === "json") {
      return NextResponse.json(logs, {
        headers: {
          "Content-Disposition": `attachment; filename="submission-logs-${new Date().toISOString().split("T")[0]}.json"`,
        },
      });
    } else {
      return NextResponse.json({ detail: "Unsupported format. Use 'csv' or 'json'." }, { status: 400 });
    }
  } catch (error) {
    return NextResponse.json(
      { detail: (error as Error).message ?? "Unable to export logs." },
      { status: 500 }
    );
  }
}

