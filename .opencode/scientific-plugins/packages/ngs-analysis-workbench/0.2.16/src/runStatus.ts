export const ACTIVE_RUN_STATUSES = [
  "starting",
  "running",
  "cancel_requested",
  "canceling",
] as const;

export const TERMINAL_RUN_STATUSES = [
  "completed",
  "failed",
  "canceled",
  "orphaned",
] as const;

export function latestActiveRunFilters(): {
  statuses: string[];
  limit: 1;
} {
  return {
    statuses: [...ACTIVE_RUN_STATUSES],
    limit: 1,
  };
}

export function isActiveRunStatus(status: string | undefined): boolean {
  return Boolean(
    status && ACTIVE_RUN_STATUSES.some((candidate) => candidate === status),
  );
}

export function isTerminalRunStatus(status: string): boolean {
  return TERMINAL_RUN_STATUSES.some((candidate) => candidate === status);
}

export type RunStatusTone =
  | "danger"
  | "info"
  | "neutral"
  | "success"
  | "warning";

export interface RunStatusPresentation {
  label: string;
  status: string;
  tone: RunStatusTone;
}

export function runStatusPresentation(status: string): RunStatusPresentation {
  return {
    label: humanizeRunStatus(status),
    status,
    tone: runStatusTone(status),
  };
}

function runStatusTone(status: string): RunStatusTone {
  if (status === "completed" || status === "already_finished") return "success";
  if (status === "failed") return "danger";
  if (
    status === "blocked" ||
    status === "canceling" ||
    status === "cancel_requested" ||
    status === "orphaned"
  )
    return "warning";
  if (status === "canceled" || status === "finished_unverified")
    return "neutral";
  return "info";
}

function humanizeRunStatus(value: string) {
  return value
    .replaceAll("_", " ")
    .replace(/^\w/, (character) => character.toUpperCase());
}
