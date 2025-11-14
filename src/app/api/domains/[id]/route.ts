import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET(req: NextRequest, { params }: { params: { id: string } }) {
  try {
    const id = parseInt(params.id);

    if (isNaN(id)) {
      return NextResponse.json({ detail: "Invalid domain ID." }, { status: 400 });
    }

    const domain = await prisma.domain.findUnique({
      where: { id },
      include: {
        templates: {
          select: {
            id: true,
            name: true,
          },
        },
      },
    });

    if (!domain) {
      return NextResponse.json({ detail: "Domain not found." }, { status: 404 });
    }

    return NextResponse.json(domain);
  } catch (error) {
    return NextResponse.json(
      { detail: (error as Error).message ?? "Unable to fetch domain." },
      { status: 500 }
    );
  }
}

export async function PUT(req: NextRequest, { params }: { params: { id: string } }) {
  try {
    const id = parseInt(params.id);

    if (isNaN(id)) {
      return NextResponse.json({ detail: "Invalid domain ID." }, { status: 400 });
    }

    const body = await req.json();
    const { url, category, isActive } = body;

    const updateData: any = {};
    if (url !== undefined) {
      try {
        new URL(url);
        updateData.url = url;
      } catch {
        return NextResponse.json({ detail: "Invalid URL format." }, { status: 400 });
      }
    }
    if (category !== undefined) updateData.category = category || null;
    if (isActive !== undefined) updateData.isActive = isActive;

    const domain = await prisma.domain.update({
      where: { id },
      data: updateData,
      include: {
        templates: {
          select: {
            name: true,
          },
        },
      },
    });

    return NextResponse.json(domain);
  } catch (error: any) {
    if (error.code === "P2025") {
      return NextResponse.json({ detail: "Domain not found." }, { status: 404 });
    }
    if (error.code === "P2002") {
      return NextResponse.json({ detail: "Domain with this URL already exists." }, { status: 409 });
    }
    return NextResponse.json(
      { detail: (error as Error).message ?? "Unable to update domain." },
      { status: 500 }
    );
  }
}

export async function DELETE(req: NextRequest, { params }: { params: { id: string } }) {
  try {
    const id = parseInt(params.id);

    if (isNaN(id)) {
      return NextResponse.json({ detail: "Invalid domain ID." }, { status: 400 });
    }

    await prisma.domain.delete({
      where: { id },
    });

    return NextResponse.json({ message: "Domain deleted successfully." });
  } catch (error: any) {
    if (error.code === "P2025") {
      return NextResponse.json({ detail: "Domain not found." }, { status: 404 });
    }
    return NextResponse.json(
      { detail: (error as Error).message ?? "Unable to delete domain." },
      { status: 500 }
    );
  }
}

