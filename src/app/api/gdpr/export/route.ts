import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const { email } = await request.json();

    if (!email) {
      return NextResponse.json(
        { error: "Email required" },
        { status: 400 }
      );
    }

    // Find all data related to this email
    const clients = await prisma.client.findMany({
      where: { email },
      include: {
        business: true,
        tracking: true,
      },
    });

    const data = {
      email,
      exportedAt: new Date().toISOString(),
      clients,
    };

    return NextResponse.json(data);
  } catch (error) {
    console.error("Error exporting GDPR data:", error);
    return NextResponse.json(
      { error: "Failed to export data" },
      { status: 500 }
    );
  }
}

