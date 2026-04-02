import { prisma } from "@/lib/prisma";

type BatchProgressCounts = {
  pending: number;
  running: number;
  success: number;
  failed: number;
  skipped: number;
  cancelled: number;
};

function summarizeRunStatus(counts: BatchProgressCounts): string {
  if (counts.running > 0) return "running";
  if (counts.pending > 0) return "pending";
  if (counts.cancelled > 0) {
    return "cancelled";
  }
  if (counts.failed > 0 && counts.success === 0 && counts.skipped === 0) {
    return "failed";
  }
  if (counts.failed > 0) return "completed_with_failures";
  return "completed";
}

export async function refreshBatchRunCounts(batchRunId: number) {
  const items = await prisma.automationBatchItem.findMany({
    where: { batchRunId },
    select: {
      status: true,
      domainId: true,
      updatedAt: true,
    },
    orderBy: {
      updatedAt: "desc",
    },
  });

  const counts: BatchProgressCounts = {
    pending: 0,
    running: 0,
    success: 0,
    failed: 0,
    skipped: 0,
    cancelled: 0,
  };

  for (const item of items) {
    const normalizedStatus = item.status.toLowerCase();
    if (normalizedStatus === "success" || normalizedStatus === "submitted" || normalizedStatus === "completed") {
      counts.success += 1;
    } else if (normalizedStatus === "failed" || normalizedStatus === "error" || normalizedStatus === "timeout") {
      counts.failed += 1;
    } else if (normalizedStatus === "skipped") {
      counts.skipped += 1;
    } else if (normalizedStatus === "cancelled") {
      counts.cancelled += 1;
    } else if (normalizedStatus === "running") {
      counts.running += 1;
    } else {
      counts.pending += 1;
    }
  }

  const latestRunningItem = items.find((item) => item.status.toLowerCase() === "running") ?? null;
  const nextStatus = summarizeRunStatus(counts);
  const processedDomains =
    counts.success + counts.failed + counts.skipped + counts.cancelled;

  return prisma.automationBatchRun.update({
    where: { id: batchRunId },
    data: {
      status: nextStatus,
      totalDomains: items.length,
      processedDomains,
      successCount: counts.success,
      failureCount: counts.failed,
      skippedCount: counts.skipped,
      pendingCount: counts.pending + counts.running,
      currentDomainId: latestRunningItem?.domainId ?? null,
      finishedAt: counts.pending === 0 && counts.running === 0 ? new Date() : null,
    },
  });
}

export async function markBatchItemRunning(batchRunItemId: number) {
  const item = await prisma.automationBatchItem.update({
    where: { id: batchRunItemId },
    data: {
      status: "running",
      attemptCount: {
        increment: 1,
      },
      startedAt: new Date(),
      finishedAt: null,
      skipReason: null,
      lastError: null,
    },
    select: {
      id: true,
      batchRunId: true,
      domainId: true,
    },
  });

  await prisma.automationBatchRun.update({
    where: { id: item.batchRunId },
    data: {
      status: "running",
      startedAt: new Date(),
      pausedAt: null,
      cancelledAt: null,
      currentDomainId: item.domainId,
      finishedAt: null,
    },
  });

  return item;
}

export async function syncBatchRunItemFromSubmissionLog(submissionId: number) {
  const submission = await prisma.submissionLog.findUnique({
    where: { id: submissionId },
    select: {
      id: true,
      status: true,
      message: true,
      finishedAt: true,
      batchRunId: true,
      batchRunItemId: true,
    },
  });

  if (!submission?.batchRunId || !submission.batchRunItemId) {
    return null;
  }

  const normalizedStatus = submission.status.toLowerCase();
  let itemStatus = "pending";
  if (normalizedStatus === "success" || normalizedStatus === "submitted" || normalizedStatus === "completed") {
    itemStatus = "success";
  } else if (normalizedStatus === "failed" || normalizedStatus === "error" || normalizedStatus === "timeout") {
    itemStatus = "failed";
  } else if (normalizedStatus === "running") {
    itemStatus = "running";
  }

  await prisma.automationBatchItem.update({
    where: { id: submission.batchRunItemId },
    data: {
      status: itemStatus,
      finishedAt: itemStatus === "running" ? null : submission.finishedAt ?? new Date(),
      lastError: itemStatus === "failed" ? submission.message : null,
    },
  });

  await refreshBatchRunCounts(submission.batchRunId);

  return submission;
}
