import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const clients = await prisma.client.findMany({
      orderBy: { createdAt: "desc" },
      include: {
        business: true,
        tracking: {
          orderBy: { timestamp: "desc" },
        },
      },
    });

    const stats = {
      total: clients.length,
      sent: clients.filter((c) => c.status !== "pending").length,
      opened: clients.filter((c) => c.emailOpenedAt).length,
      clicked: clients.filter((c) => c.lastClickedAt).length,
    };

    return NextResponse.json({ clients, stats });
  } catch (error) {
    console.error("Error fetching clients:", error);
    return NextResponse.json(
      { error: "Failed to fetch clients" },
      { status: 500 }
    );
  }
}

