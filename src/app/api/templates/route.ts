import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const domainId = searchParams.get("domainId");

    const templates = await prisma.template.findMany({
      where: domainId ? { domainId: parseInt(domainId) } : undefined,
      include: {
        domain: {
          select: {
            id: true,
            url: true,
          },
        },
      },
      orderBy: {
        createdAt: "desc",
      },
    });

    return NextResponse.json(templates);
  } catch (error) {
    return NextResponse.json(
      { detail: (error as Error).message ?? "Unable to fetch templates." },
      { status: 500 }
    );
  }
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { name, description, fieldMappings, domainId } = body;

    if (!name || typeof name !== "string") {
      return NextResponse.json({ detail: "Name is required." }, { status: 400 });
    }

    if (!fieldMappings || typeof fieldMappings !== "object") {
      return NextResponse.json({ detail: "Field mappings is required." }, { status: 400 });
    }

    const template = await prisma.template.create({
      data: {
        name,
        description: description || null,
        fieldMappings: fieldMappings,
        domainId: domainId ? parseInt(domainId) : null,
      },
      include: {
        domain: {
          select: {
            id: true,
            url: true,
          },
        },
      },
    });

    return NextResponse.json(template, { status: 201 });
  } catch (error: any) {
    if (error.code === "P2002") {
      return NextResponse.json({ detail: "Template with this name already exists." }, { status: 409 });
    }
    return NextResponse.json(
      { detail: (error as Error).message ?? "Unable to create template." },
      { status: 500 }
    );
  }
}

