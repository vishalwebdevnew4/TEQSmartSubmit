import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const deployments = await prisma.deploymentLog.findMany({
      orderBy: { createdAt: "desc" },
      include: {
        business: true,
        templateVersion: true,
      },
    });

    return NextResponse.json(deployments);
  } catch (error) {
    console.error("Error fetching deployments:", error);
    return NextResponse.json(
      { error: "Failed to fetch deployments" },
      { status: 500 }
    );
  }
}

