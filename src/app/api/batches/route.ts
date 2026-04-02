import { NextRequest, NextResponse } from "next/server";

import { prisma } from "@/lib/prisma";

export const runtime = "nodejs";

type IncomingBatchItem = {
  domainId: number;
  templateId?: number | null;
};

function normalizeInteger(value: unknown) {
  if (typeof value === "number" && Number.isInteger(value)) return value;
  if (typeof value === "string" && value.trim().length > 0) {
    const parsed = Number(value);
    if (!Number.isNaN(parsed) && Number.isInteger(parsed)) return parsed;
  }
  return null;
}

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const status = searchParams.get("status");
    const limit = normalizeInteger(searchParams.get("limit")) ?? 20;

    const where = status ? { status } : {};

    const runs = await prisma.automationBatchRun.findMany({
      where,
      include: {
        startedByAdmin: {
          select: {
            id: true,
            username: true,
          },
        },
        currentDomain: {
          select: {
            id: true,
            url: true,
            contactPageUrl: true,
          },
        },
        _count: {
          select: {
            items: true,
            submissions: true,
          },
        },
      },
      orderBy: {
        createdAt: "desc",
      },
      take: Math.min(limit, 100),
    });

    return NextResponse.json({ runs });
  } catch (error) {
    console.error("[Batches API] Failed to fetch runs:", error);
    return NextResponse.json(
      {
        detail: error instanceof Error ? error.message : "Failed to fetch batch runs",
      },
      { status: 500 }
    );
  }
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const rawItems = Array.isArray(body?.items) ? body.items : [];
    const batchSize = normalizeInteger(body?.batchSize) ?? 10;
    const delaySeconds = normalizeInteger(body?.delaySeconds) ?? 5;
    const retryLimit = normalizeInteger(body?.retryLimit) ?? 2;
    const startedByAdminId = normalizeInteger(body?.adminId);
    const mode = typeof body?.mode === "string" && body.mode.trim() ? body.mode.trim() : "bulk";
    const source = typeof body?.source === "string" && body.source.trim() ? body.source.trim() : "dashboard";
    const notes = typeof body?.notes === "string" && body.notes.trim() ? body.notes.trim() : null;

    const parsedItems: IncomingBatchItem[] = rawItems
      .map((item: unknown) => {
        if (!item || typeof item !== "object") return null;
        const record = item as Record<string, unknown>;
        const domainId = normalizeInteger(record.domainId);
        if (!domainId) return null;
        return {
          domainId,
          templateId: normalizeInteger(record.templateId),
        };
      })
      .filter((item: IncomingBatchItem | null): item is IncomingBatchItem => item !== null);

    const items = Array.from(
      new Map(parsedItems.map((item) => [item.domainId, item])).values()
    );

    if (items.length === 0) {
      return NextResponse.json(
        { detail: "At least one batch item with a valid domainId is required." },
        { status: 400 }
      );
    }

    const domainIds = [...new Set(items.map((item) => item.domainId))];
    const existingDomains = await prisma.domain.findMany({
      where: {
        id: {
          in: domainIds,
        },
      },
      select: {
        id: true,
      },
    });

    const existingDomainIds = new Set(existingDomains.map((domain) => domain.id));
    const missingDomainIds = domainIds.filter((domainId) => !existingDomainIds.has(domainId));

    if (missingDomainIds.length > 0) {
      return NextResponse.json(
        {
          detail: `Some domains were not found: ${missingDomainIds.join(", ")}`,
          missingDomainIds,
        },
        { status: 400 }
      );
    }

    const createdRun = await prisma.$transaction(async (tx) => {
      const run = await tx.automationBatchRun.create({
        data: {
          status: "pending",
          mode,
          source,
          notes,
          batchSize,
          delaySeconds,
          retryLimit,
          totalDomains: items.length,
          pendingCount: items.length,
          startedByAdminId,
        },
      });

      await tx.automationBatchItem.createMany({
        data: items.map((item, index) => ({
          batchRunId: run.id,
          domainId: item.domainId,
          templateId: item.templateId ?? null,
          sequence: index + 1,
          status: "pending",
        })),
      });

      return tx.automationBatchRun.findUnique({
        where: { id: run.id },
        include: {
          _count: {
            select: {
              items: true,
            },
          },
        },
      });
    });

    return NextResponse.json(
      {
        message: "Batch run created successfully.",
        run: createdRun,
      },
      { status: 201 }
    );
  } catch (error) {
    console.error("[Batches API] Failed to create run:", error);
    return NextResponse.json(
      {
        detail: error instanceof Error ? error.message : "Failed to create batch run",
      },
      { status: 500 }
    );
  }
}
