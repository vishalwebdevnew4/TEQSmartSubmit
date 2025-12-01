import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET(req: NextRequest, { params }: { params: { id: string } }) {
  try {
    const id = parseInt(params.id);

    if (isNaN(id)) {
      return NextResponse.json({ detail: "Invalid template ID." }, { status: 400 });
    }

    const template = await prisma.template.findUnique({
      where: { id },
      include: {
        domain: {
          select: {
            id: true,
            url: true,
          },
        },
        business: {
          select: {
            id: true,
            name: true,
          },
        },
        versions: {
          orderBy: { version: "desc" },
        },
      },
    });

    if (!template) {
      return NextResponse.json({ detail: "Template not found." }, { status: 404 });
    }

    return NextResponse.json(template);
  } catch (error) {
    return NextResponse.json(
      { detail: (error as Error).message ?? "Unable to fetch template." },
      { status: 500 }
    );
  }
}

export async function PUT(req: NextRequest, { params }: { params: { id: string } }) {
  try {
    const id = parseInt(params.id);

    if (isNaN(id)) {
      return NextResponse.json({ detail: "Invalid template ID." }, { status: 400 });
    }

    const body = await req.json();
    const { name, description, fieldMappings, domainId } = body;

    const updateData: any = {};
    if (name !== undefined) updateData.name = name;
    if (description !== undefined) updateData.description = description || null;
    if (fieldMappings !== undefined) updateData.fieldMappings = fieldMappings;
    if (domainId !== undefined) updateData.domainId = domainId ? parseInt(domainId) : null;

    const template = await prisma.template.update({
      where: { id },
      data: updateData,
      include: {
        domain: {
          select: {
            id: true,
            url: true,
          },
        },
      },
    });

    return NextResponse.json(template);
  } catch (error: any) {
    if (error.code === "P2025") {
      return NextResponse.json({ detail: "Template not found." }, { status: 404 });
    }
    if (error.code === "P2002") {
      return NextResponse.json({ detail: "Template with this name already exists." }, { status: 409 });
    }
    return NextResponse.json(
      { detail: (error as Error).message ?? "Unable to update template." },
      { status: 500 }
    );
  }
}

export async function DELETE(req: NextRequest, { params }: { params: { id: string } }) {
  try {
    const id = parseInt(params.id);

    if (isNaN(id)) {
      return NextResponse.json({ detail: "Invalid template ID." }, { status: 400 });
    }

    await prisma.template.delete({
      where: { id },
    });

    return NextResponse.json({ message: "Template deleted successfully." });
  } catch (error: any) {
    if (error.code === "P2025") {
      return NextResponse.json({ detail: "Template not found." }, { status: 404 });
    }
    return NextResponse.json(
      { detail: (error as Error).message ?? "Unable to delete template." },
      { status: 500 }
    );
  }
}

