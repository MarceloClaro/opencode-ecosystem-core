import type {
  AttemptCounts,
  ExecutionObservation,
  ExecutionProcess,
  ExecutionTaskAttempt,
} from "./model";

export function parseExecutionObservation(value: unknown): ExecutionObservation | undefined {
  if (!isRecord(value) || value.schema_version !== 1 || typeof value.engine !== "string") return undefined;
  if (!isRecord(value.evidence) || !isRecord(value.counts) || !isRecord(value.progress)) return undefined;
  if (!isRecord(value.structure) || !Array.isArray(value.structure.processes) || !Array.isArray(value.attempts)) return undefined;

  const counts = parseCounts(value.counts);
  const processes = value.structure.processes.flatMap(parseProcess);
  const attempts = value.attempts.flatMap(parseAttempt);
  if (!counts || processes.length !== value.structure.processes.length || attempts.length !== value.attempts.length) {
    return undefined;
  }

  return {
    schema_version: 1,
    engine: value.engine,
    evidence: {
      kind: stringValue(value.evidence.kind),
      path: nullableString(value.evidence.path),
      available: value.evidence.available === true,
      append_only: value.evidence.append_only === true,
      coverage: stringValue(value.evidence.coverage),
      reason: nullableString(value.evidence.reason),
      record_count: nullableNumber(value.evidence.record_count),
      ignored_record_count: numberValue(value.evidence.ignored_record_count),
    },
    counts,
    count_unit: "task_attempts",
    progress: {
      completed: numberValue(value.progress.completed),
      finished_attempts: nullableNumber(value.progress.finished_attempts),
      total: nullableNumber(value.progress.total),
      determinate: value.progress.determinate === true,
      reason: nullableString(value.progress.reason),
    },
    structure: {
      kind: "discovered_processes",
      semantic_stages: false,
      ordering: stringValue(value.structure.ordering),
      processes,
    },
    attempts_truncated: value.attempts_truncated === true,
    attempts,
  };
}

function parseCounts(value: Record<string, unknown>): AttemptCounts | undefined {
  const fields = ["total", "queued", "running", "completed", "cached", "failed", "aborted", "unknown"] as const;
  if (fields.some((field) => typeof value[field] !== "number")) return undefined;
  return {
    total: numberValue(value.total),
    queued: numberValue(value.queued),
    running: numberValue(value.running),
    completed: numberValue(value.completed),
    cached: numberValue(value.cached),
    failed: numberValue(value.failed),
    aborted: numberValue(value.aborted),
    unknown: numberValue(value.unknown),
  };
}

function parseProcess(value: unknown): ExecutionProcess[] {
  if (!isRecord(value) || typeof value.name !== "string" || typeof value.label !== "string" || !isRecord(value.counts)) return [];
  const counts = parseCounts(value.counts);
  return counts ? [{ name: value.name, label: value.label, counts }] : [];
}

function parseAttempt(value: unknown): ExecutionTaskAttempt[] {
  if (
    !isRecord(value)
    || typeof value.attempt_id !== "string"
    || (
      value.attempt_number !== undefined
      && value.attempt_number !== null
      && typeof value.attempt_number !== "number"
    )
    || typeof value.process !== "string"
    || typeof value.process_label !== "string"
    || typeof value.state !== "string"
  ) return [];
  return [{
    attempt_id: value.attempt_id,
    attempt_number: nullableNumber(value.attempt_number),
    task_id: nullableString(value.task_id),
    task_hash: nullableString(value.task_hash),
    native_id: nullableString(value.native_id),
    process: value.process,
    process_label: value.process_label,
    sample_or_shard: nullableString(value.sample_or_shard),
    state: value.state,
    exit_code: nullableNumber(value.exit_code),
    submitted_at: nullableString(value.submitted_at),
    started_at: nullableString(value.started_at),
    completed_at: nullableString(value.completed_at),
    duration: nullableString(value.duration),
    realtime: nullableString(value.realtime),
    cpu: nullableString(value.cpu),
    peak_rss: nullableString(value.peak_rss),
    peak_vmem: nullableString(value.peak_vmem),
    workdir: nullableString(value.workdir),
    container: nullableString(value.container),
  }];
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function stringValue(value: unknown) {
  return typeof value === "string" ? value : "";
}

function nullableString(value: unknown) {
  return typeof value === "string" ? value : null;
}

function nullableNumber(value: unknown) {
  return typeof value === "number" ? value : null;
}

function numberValue(value: unknown) {
  return typeof value === "number" ? value : 0;
}
