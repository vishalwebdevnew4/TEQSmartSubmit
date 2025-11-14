import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const isActive = searchParams.get("isActive");
    const limit = searchParams.get("limit");
    const offset = searchParams.get("offset");

    const where: any = {};
    if (isActive !== null && isActive !== undefined) {
      where.isActive = isActive === "true";
    }

    const take = limit ? parseInt(limit) : 100;
    const skip = offset ? parseInt(offset) : 0;

    const domains = await prisma.domain.findMany({
      where,
      include: {
        templates: {
          select: {
            name: true,
          },
          take: 3,
        },
      },
      orderBy: {
        createdAt: "desc",
      },
      take,
      skip,
    });

    return NextResponse.json(domains);
  } catch (error) {
    return NextResponse.json(
      { detail: (error as Error).message ?? "Unable to fetch domains." },
      { status: 500 }
    );
  }
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { url, category, isActive } = body;

    if (!url || typeof url !== "string") {
      return NextResponse.json({ detail: "URL is required." }, { status: 400 });
    }

    // Validate URL format
    try {
      new URL(url);
    } catch {
      return NextResponse.json({ detail: "Invalid URL format." }, { status: 400 });
    }

    const domain = await prisma.domain.create({
      data: {
        url,
        category: category || null,
        isActive: isActive !== undefined ? isActive : true,
      },
      include: {
        templates: {
          select: {
            name: true,
          },
        },
      },
    });

    return NextResponse.json(domain, { status: 201 });
  } catch (error: any) {
    if (error.code === "P2002") {
      return NextResponse.json({ detail: "Domain with this URL already exists." }, { status: 409 });
    }
    return NextResponse.json(
      { detail: (error as Error).message ?? "Unable to create domain." },
      { status: 500 }
    );
  }
}

export async function PUT(req: NextRequest) {
  try {
    const body = await req.json();
    const { ids, isActive } = body;

    if (!Array.isArray(ids) || ids.length === 0) {
      return NextResponse.json({ detail: "IDs array is required." }, { status: 400 });
    }

    if (typeof isActive !== "boolean") {
      return NextResponse.json({ detail: "isActive must be a boolean." }, { status: 400 });
    }

    const result = await prisma.domain.updateMany({
      where: {
        id: {
          in: ids.map((id: any) => parseInt(id)),
        },
      },
      data: {
        isActive,
      },
    });

    return NextResponse.json({ count: result.count, message: "Domains updated successfully." });
  } catch (error) {
    return NextResponse.json(
      { detail: (error as Error).message ?? "Unable to bulk update domains." },
      { status: 500 }
    );
  }
}

