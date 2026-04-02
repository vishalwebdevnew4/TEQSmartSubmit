import { NextRequest, NextResponse } from "next/server";

import { refreshBatchRunCounts } from "@/lib/automation-batches";
import { prisma } from "@/lib/prisma";

export const runtime = "nodejs";

function normalizeInteger(value: unknown) {
  if (typeof value === "number" && Number.isInteger(value)) return value;
  if (typeof value === "string" && value.trim().length > 0) {
    const parsed = Number(value);
    if (!Number.isNaN(parsed) && Number.isInteger(parsed)) return parsed;
  }
  return null;
}

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const batchRunId = normalizeInteger(id);

    if (!batchRunId) {
      return NextResponse.json({ detail: "Invalid batch run id." }, { status: 400 });
    }

    const run = await prisma.automationBatchRun.findUnique({
      where: { id: batchRunId },
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
        items: {
          include: {
            domain: {
              select: {
                id: true,
                url: true,
                contactPageUrl: true,
              },
            },
            template: {
              select: {
                id: true,
                name: true,
              },
            },
            submissions: {
              select: {
                id: true,
                status: true,
                createdAt: true,
                finishedAt: true,
              },
              orderBy: {
                createdAt: "desc",
              },
              take: 3,
            },
          },
          orderBy: {
            sequence: "asc",
          },
        },
      },
    });

    if (!run) {
      return NextResponse.json({ detail: "Batch run not found." }, { status: 404 });
    }

    return NextResponse.json({ run });
  } catch (error) {
    console.error("[Batch Detail API] Failed to fetch run:", error);
    return NextResponse.json(
      {
        detail: error instanceof Error ? error.message : "Failed to fetch batch run",
      },
      { status: 500 }
    );
  }
}

export async function PATCH(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const batchRunId = normalizeInteger(id);

    if (!batchRunId) {
      return NextResponse.json({ detail: "Invalid batch run id." }, { status: 400 });
    }

    const body = await req.json();
    const action = typeof body?.action === "string" ? body.action.trim().toLowerCase() : "";

    if (!action) {
      return NextResponse.json({ detail: "Field 'action' is required." }, { status: 400 });
    }

    const existingRun = await prisma.automationBatchRun.findUnique({
      where: { id: batchRunId },
      select: {
        id: true,
        status: true,
      },
    });

    if (!existingRun) {
      return NextResponse.json({ detail: "Batch run not found." }, { status: 404 });
    }

    let updatedRun;

    if (action === "pause") {
      updatedRun = await prisma.automationBatchRun.update({
        where: { id: batchRunId },
        data: {
          status: "paused",
          pausedAt: new Date(),
          currentDomainId: null,
        },
      });
    } else if (action === "resume") {
      await prisma.automationBatchItem.updateMany({
        where: {
          batchRunId,
          status: "running",
        },
        data: {
          status: "pending",
        },
      });

      updatedRun = await prisma.automationBatchRun.update({
        where: { id: batchRunId },
        data: {
          status: "pending",
          pausedAt: null,
          finishedAt: null,
          cancelledAt: null,
          currentDomainId: null,
        },
      });

      updatedRun = await refreshBatchRunCounts(batchRunId);
    } else if (action === "cancel") {
      await prisma.automationBatchItem.updateMany({
        where: {
          batchRunId,
          status: {
            in: ["pending", "running"],
          },
        },
        data: {
          status: "cancelled",
          finishedAt: new Date(),
        },
      });

      updatedRun = await prisma.automationBatchRun.update({
        where: { id: batchRunId },
        data: {
          status: "cancelled",
          cancelledAt: new Date(),
          currentDomainId: null,
        },
      });

      updatedRun = await refreshBatchRunCounts(batchRunId);
    } else if (action === "refresh") {
      updatedRun = await refreshBatchRunCounts(batchRunId);
    } else {
      return NextResponse.json(
        { detail: `Unsupported action '${action}'.` },
        { status: 400 }
      );
    }

    return NextResponse.json({
      message: `Batch run ${action} action applied.`,
      run: updatedRun,
    });
  } catch (error) {
    console.error("[Batch Detail API] Failed to update run:", error);
    return NextResponse.json(
      {
        detail: error instanceof Error ? error.message : "Failed to update batch run",
      },
      { status: 500 }
    );
  }
}
