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

    // Support fetching all domains by allowing high limit (default to 10000)
    const take = limit ? parseInt(limit) : 10000;
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

    // Fetch latest contact check messages for domains with error status
    const domainIds = domains.map(d => d.id);
    let errorMessageMap = new Map<number, string | null>();
    
    if (domainIds.length > 0) {
      try {
        // Use $queryRaw to fetch contact check messages
        const contactChecks = await prisma.$queryRaw<Array<{ domainId: bigint; message: string | null }>>`
          SELECT DISTINCT ON ("domainId") "domainId", "message"
          FROM "ContactCheck"
          WHERE "domainId" = ANY(ARRAY[${domainIds.join(',')}]::int[])
            AND "status" = 'error'
          ORDER BY "domainId", "checkedAt" DESC
        `;
        
        errorMessageMap = new Map(
          contactChecks.map((check) => [Number(check.domainId), check.message])
        );
      } catch (error) {
        // If query fails, continue without error messages
        console.error("Failed to fetch contact check messages:", error);
      }
    }

    // Add latest error message to each domain
    const domainsWithErrorMessages = domains.map((domain) => {
      return {
        ...domain,
        contactCheckMessage: errorMessageMap.get(domain.id) || null,
      };
    });

    return NextResponse.json(domainsWithErrorMessages);
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
          contactCheckStatus: "pending",
        } as any,
      include: {
        templates: {
          select: {
            name: true,
          },
        },
      },
    });

    // Check contact page in background (don't await)
    (async () => {
      try {
        const { detectContactPage } = await import("@/lib/contact-page-detector");
        const checkResult = await detectContactPage(domain.url);
        
        await prisma.domain.update({
          where: { id: domain.id },
          data: {
            contactPageUrl: checkResult.contactUrl,
            contactCheckStatus: checkResult.status,
            contactCheckedAt: new Date(),
          } as any,
        });

        await (prisma as any).contactCheck.create({
          data: {
            domainId: domain.id,
            status: checkResult.status,
            contactUrl: checkResult.contactUrl,
            message: checkResult.message,
          },
        });
      } catch (error: any) {
        console.error(`Error checking contact page for ${domain.url}:`, error.message || error);
        // Update domain with error status
        try {
          await prisma.domain.update({
            where: { id: domain.id },
            data: {
              contactCheckStatus: "error",
              contactCheckedAt: new Date(),
            } as any,
          });

          await (prisma as any).contactCheck.create({
            data: {
              domainId: domain.id,
              status: "error",
              contactUrl: null,
              message: error.message || "Unknown error during contact page check",
            },
          });
        } catch (dbError) {
          console.error(`Failed to update error status for domain ${domain.id}:`, dbError);
        }
      }
    })();

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

export async function DELETE(req: NextRequest) {
  try {
    const body = await req.json();
    const { ids } = body;

    if (!Array.isArray(ids) || ids.length === 0) {
      return NextResponse.json({ detail: "IDs array is required." }, { status: 400 });
    }

    const domainIds = ids.map((id: any) => parseInt(id)).filter((id) => !isNaN(id));

    if (domainIds.length === 0) {
      return NextResponse.json({ detail: "No valid domain IDs provided." }, { status: 400 });
    }

    const result = await prisma.domain.deleteMany({
      where: {
        id: {
          in: domainIds,
        },
      },
    });

    return NextResponse.json({
      count: result.count,
      message: `Successfully deleted ${result.count} domain(s).`,
    });
  } catch (error) {
    return NextResponse.json(
      { detail: (error as Error).message ?? "Unable to bulk delete domains." },
      { status: 500 }
    );
  }
}

