import type { ChildProcessByStdio } from "node:child_process";
import type { Readable } from "node:stream";

type StopReason = "pause" | "cancel";
type ManagedChildProcess = ChildProcessByStdio<null, Readable, Readable>;

type RunningSubmission = {
  process: ManagedChildProcess;
  tempDir: string;
  stopReason: StopReason | null;
};

const runningSubmissions = new Map<number, RunningSubmission>();

export function registerRunningSubmission(
  submissionId: number,
  process: ManagedChildProcess,
  tempDir: string
) {
  runningSubmissions.set(submissionId, {
    process,
    tempDir,
    stopReason: null,
  });
}

export function getRunningSubmission(submissionId: number) {
  return runningSubmissions.get(submissionId) ?? null;
}

export function getSubmissionStopReason(submissionId: number) {
  return runningSubmissions.get(submissionId)?.stopReason ?? null;
}

export function clearRunningSubmission(submissionId: number) {
  runningSubmissions.delete(submissionId);
}

export function stopRunningSubmission(submissionId: number, reason: StopReason) {
  const running = runningSubmissions.get(submissionId);
  if (!running) {
    return false;
  }

  running.stopReason = reason;

  try {
    running.process.kill("SIGTERM");
  } catch (error) {
    console.error(`[AUTOMATION] Failed to stop submission ${submissionId}:`, error);
  }

  return true;
}
