import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { cache, cacheKeys, cached } from "@/lib/cache";

export const dynamic = 'force-dynamic';
export const revalidate = 0;

export async function GET(req: NextRequest) {
  try {
    // Get all stats in parallel with caching
    const [
      totalDomains,
      activeDomains,
      domainsWithForms,
      totalSubmissions,
      successSubmissions,
      failedSubmissions,
      recentActivity,
    ] = await Promise.all([
      cached(cacheKeys.dashboardStats(), () => prisma.domain.count().catch(() => 0), 30),
      cached(cacheKeys.dashboardStats() + ":active", () => prisma.domain.count({ where: { isActive: true } }).catch(() => 0), 30),
      cached(cacheKeys.dashboardStats() + ":forms", async () => {
        const domains = await prisma.domain.findMany({
          where: { isActive: true },
          select: { contactCheckStatus: true },
        }).catch(() => []);
        return domains.filter((d: any) => d.contactCheckStatus === "found").length;
      }, 30),
      cached(cacheKeys.dashboardStats() + ":total", () => prisma.submissionLog.count().catch(() => 0), 30),
      cached(cacheKeys.dashboardStats() + ":success", () => prisma.submissionLog.count({ where: { status: "success" } }).catch(() => 0), 30),
      cached(cacheKeys.dashboardStats() + ":failed", () => prisma.submissionLog.count({ where: { status: "failed" } }).catch(() => 0), 30),
      cached(cacheKeys.dashboardStats() + ":activity", () => prisma.submissionLog.findMany({
        orderBy: { createdAt: "desc" },
        take: 10,
        include: {
          domain: {
            select: {
              id: true,
              url: true,
            },
          },
        },
      }).catch(() => []), 10),
    ]);

    const successRate = totalSubmissions > 0 
      ? Math.round((successSubmissions / totalSubmissions) * 100) 
      : 0;

    return NextResponse.json({
      totalDomains,
      activeDomains,
      domainsWithForms,
      totalSubmissions,
      successSubmissions,
      failedSubmissions,
      successRate,
      recentActivity,
    });
  } catch (error) {
    console.error("[Stats API] Error:", error);
    return NextResponse.json(
      { 
        detail: error instanceof Error ? error.message : "Failed to fetch stats",
        error: "Internal server error"
      },
      { status: 500 }
    );
  }
}

