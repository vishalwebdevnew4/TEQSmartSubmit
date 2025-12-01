import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const type = searchParams.get("type") || "all";
    const limit = parseInt(searchParams.get("limit") || "50");

    const notifications: any[] = [];

    // Error notifications
    if (type === "all" || type === "errors") {
      const failedTasks = await prisma.task.findMany({
        where: { status: "failed" },
        orderBy: { createdAt: "desc" },
        take: limit,
        include: { business: true },
      });

      for (const task of failedTasks) {
        notifications.push({
          id: `task-${task.id}`,
          type: "error",
          title: `Task Failed: ${task.taskType}`,
          message: task.errorMessage || "Unknown error",
          timestamp: task.createdAt,
          link: `/tasks/${task.id}`,
        });
      }
    }

    // Engagement notifications
    if (type === "all" || type === "engagement") {
      const recentClicks = await prisma.clientTracking.findMany({
        where: { eventType: "link_clicked" },
        orderBy: { timestamp: "desc" },
        take: limit,
        include: { client: { include: { business: true } } },
      });

      for (const tracking of recentClicks) {
        notifications.push({
          id: `click-${tracking.id}`,
          type: "engagement",
          title: "Client Clicked Link",
          message: `${tracking.client.email} clicked on ${tracking.client.business.name}`,
          timestamp: tracking.timestamp,
          link: `/clients/${tracking.clientId}`,
        });
      }
    }

    // Deployment notifications
    if (type === "all" || type === "deployments") {
      const recentDeployments = await prisma.deploymentLog.findMany({
        where: { status: { in: ["success", "failed"] } },
        orderBy: { createdAt: "desc" },
        take: limit,
        include: { business: true },
      });

      for (const deployment of recentDeployments) {
        notifications.push({
          id: `deploy-${deployment.id}`,
          type: deployment.status === "success" ? "success" : "error",
          title: `Deployment ${deployment.status}`,
          message: `${deployment.business.name} - ${deployment.vercelUrl || "No URL"}`,
          timestamp: deployment.createdAt,
          link: `/deployments/${deployment.id}`,
        });
      }
    }

    // Sort by timestamp
    notifications.sort((a, b) => 
      new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );

    return NextResponse.json(notifications.slice(0, limit));
  } catch (error) {
    console.error("Error fetching notifications:", error);
    return NextResponse.json(
      { error: "Failed to fetch notifications" },
      { status: 500 }
    );
  }
}

