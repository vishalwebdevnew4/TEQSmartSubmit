import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const withVersions = searchParams.get("withVersions") === "true";
    
    const templates = await prisma.template.findMany({
      orderBy: { createdAt: "desc" },
      include: {
        business: true,
        domain: true,
        versions: withVersions
          ? {
              orderBy: { version: "desc" },
            }
          : {
              where: { isActive: true },
              take: 1,
            },
      },
    });

    return NextResponse.json(templates);
  } catch (error) {
    console.error("Error fetching templates:", error);
    return NextResponse.json(
      { error: "Failed to fetch templates" },
      { status: 500 }
    );
  }
}
