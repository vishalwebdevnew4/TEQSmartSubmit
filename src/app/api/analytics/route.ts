import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    // Get all stats
    const [
      totalBusinesses,
      activeDeployments,
      totalClients,
      deployments,
      clients,
      submissions,
    ] = await Promise.all([
      prisma.business.count(),
      prisma.deploymentLog.count({ where: { status: "success" } }),
      prisma.client.count(),
      prisma.deploymentLog.findMany({
        select: { status: true },
      }),
      prisma.client.findMany({
        select: { status: true },
      }),
      prisma.formSubmissionLog.findMany({
        where: {
          createdAt: {
            gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // Last 30 days
          },
        },
        select: { status: true, createdAt: true },
      }),
    ]);

    // Calculate submission success rate
    const totalSubmissions = submissions.length;
    const successfulSubmissions = submissions.filter((s) => s.status === "success").length;
    const submissionSuccessRate = totalSubmissions > 0
      ? Math.round((successfulSubmissions / totalSubmissions) * 100)
      : 0;

    // Deployment status breakdown
    const deploymentStatusMap: Record<string, number> = {};
    deployments.forEach((d) => {
      deploymentStatusMap[d.status] = (deploymentStatusMap[d.status] || 0) + 1;
    });
    const deploymentStatus = Object.entries(deploymentStatusMap).map(([name, value]) => ({
      name,
      value,
    }));

    // Client engagement breakdown
    const clientEngagementMap: Record<string, number> = {};
    clients.forEach((c) => {
      clientEngagementMap[c.status] = (clientEngagementMap[c.status] || 0) + 1;
    });
    const clientEngagement = Object.entries(clientEngagementMap).map(([status, count]) => ({
      status,
      count,
    }));

    // Submission trends (last 30 days)
    const trendsMap: Record<string, { success: number; failed: number }> = {};
    submissions.forEach((s) => {
      const date = new Date(s.createdAt).toISOString().split("T")[0];
      if (!trendsMap[date]) {
        trendsMap[date] = { success: 0, failed: 0 };
      }
      if (s.status === "success") {
        trendsMap[date].success++;
      } else {
        trendsMap[date].failed++;
      }
    });
    const submissionTrends = Object.entries(trendsMap)
      .map(([date, data]) => ({ date, ...data }))
      .sort((a, b) => a.date.localeCompare(b.date));

    return NextResponse.json({
      totalBusinesses,
      activeDeployments,
      totalClients,
      submissionSuccessRate,
      deploymentStatus,
      clientEngagement,
      submissionTrends,
    });
  } catch (error) {
    console.error("Error fetching analytics:", error);
    return NextResponse.json(
      { error: "Failed to fetch analytics" },
      { status: 500 }
    );
  }
}

