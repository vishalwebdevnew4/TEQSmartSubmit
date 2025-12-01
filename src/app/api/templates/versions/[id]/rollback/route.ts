import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export const dynamic = "force-dynamic";

export async function POST(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const versionId = parseInt(params.id);

    // Get version
    const version = await prisma.templateVersion.findUnique({
      where: { id: versionId },
      include: { template: true },
    });

    if (!version) {
      return NextResponse.json(
        { success: false, error: "Version not found" },
        { status: 404 }
      );
    }

    // Deactivate all versions
    await prisma.templateVersion.updateMany({
      where: { templateId: version.templateId },
      data: { isActive: false },
    });

    // Activate this version
    await prisma.templateVersion.update({
      where: { id: versionId },
      data: { isActive: true },
    });

    return NextResponse.json({ success: true });
  } catch (error: any) {
    console.error("Error rolling back version:", error);
    return NextResponse.json(
      { success: false, error: error.message || "Failed to rollback" },
      { status: 500 }
    );
  }
}

