import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export const dynamic = "force-dynamic";

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const templateId = parseInt(params.id);

    const versions = await prisma.templateVersion.findMany({
      where: { templateId },
      orderBy: { version: "desc" },
      include: {
        template: {
          include: {
            business: true,
          },
        },
      },
    });

    return NextResponse.json(versions);
  } catch (error) {
    console.error("Error fetching template versions:", error);
    return NextResponse.json(
      { error: "Failed to fetch versions" },
      { status: 500 }
    );
  }
}

