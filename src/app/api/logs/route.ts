import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export const runtime = "nodejs";

export async function DELETE(req: NextRequest) {
  try {
    // Test database connection first
    try {
      await prisma.$connect();
    } catch (dbError) {
      console.error("Database connection error:", dbError);
      return NextResponse.json(
        { 
          detail: `Database connection failed: ${(dbError as Error).message}`,
          error: "DATABASE_CONNECTION_ERROR"
        },
        { status: 500 }
      );
    }

    // Delete all submission logs
    const result = await prisma.submissionLog.deleteMany({});

    return NextResponse.json({
      success: true,
      message: `Successfully deleted ${result.count} log(s)`,
      deletedCount: result.count,
    });
  } catch (error) {
    console.error("Error clearing logs:", error);
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    
    return NextResponse.json(
      { 
        detail: `Unable to clear logs: ${errorMessage}`,
        error: "CLEAR_LOGS_ERROR"
      },
      { status: 500 }
    );
  }
}

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const status = searchParams.get("status");
    const domainId = searchParams.get("domainId");
    const templateId = searchParams.get("templateId");
    const limit = searchParams.get("limit");
    const offset = searchParams.get("offset");

    const where: any = {};
    if (status) where.status = status;
    if (domainId) where.domainId = parseInt(domainId);
    if (templateId) where.templateId = parseInt(templateId);

    const take = limit ? parseInt(limit) : 50;
    const skip = offset ? parseInt(offset) : 0;

    // Test database connection first
    try {
      await prisma.$connect();
    } catch (dbError) {
      console.error("Database connection error:", dbError);
      return NextResponse.json(
        { 
          detail: `Database connection failed: ${(dbError as Error).message}`,
          error: "DATABASE_CONNECTION_ERROR"
        },
        { status: 500 }
      );
    }

    const [logs, total] = await Promise.all([
      prisma.submissionLog.findMany({
        where,
        include: {
          domain: {
            select: {
              id: true,
              url: true,
            },
          },
          template: {
            select: {
              id: true,
              name: true,
            },
          },
        },
        orderBy: {
          createdAt: "desc",
        },
        take,
        skip,
      }),
      prisma.submissionLog.count({ where }),
    ]);

    // Log for debugging (only in development or if explicitly enabled)
    if (process.env.NODE_ENV === "development" || process.env.DEBUG_LOGS === "true") {
      console.log(`[API /logs] Fetched ${logs.length} logs (total: ${total})`);
    }

    return NextResponse.json({
      logs,
      total,
      limit: take,
      offset: skip,
    });
  } catch (error) {
    console.error("Error fetching logs:", error);
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    const errorStack = error instanceof Error ? error.stack : undefined;
    
    return NextResponse.json(
      { 
        detail: `Unable to fetch logs: ${errorMessage}`,
        error: "FETCH_LOGS_ERROR",
        ...(process.env.NODE_ENV === "development" && { stack: errorStack })
      },
      { status: 500 }
    );
  }
}

