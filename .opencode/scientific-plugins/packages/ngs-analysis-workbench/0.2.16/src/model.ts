import type { AnalysisReportData } from "./report/types";

export interface Pipeline {
  id: string;
  title: string;
  workflow: string;
  description: string;
  engine?: "nextflow" | "snakemake";
  collection?: string;
  catalog?: "bundled" | "saved";
  sourceKind?: "local" | "remote";
  revision?: string;
  entrypoint?: string;
  sourceSha256?: string;
}

export interface ComputeTargetRef {
  target_id: string;
  provider: string;
  config_hash?: string;
}

export interface ComputeTarget {
  target_id: string;
  title: string;
  controllerTransport: string;
  executor: string;
  workspaceAccess: string;
  description: string;
  workspaceRoot?: string;
  executorConfiguration: Record<string, string>;
}

export interface OperationResult {
  ok: boolean;
  errors?: string[];
  readiness?: unknown;
}

export interface AttemptCounts {
  total: number;
  queued: number;
  running: number;
  completed: number;
  cached: number;
  failed: number;
  aborted: number;
  unknown: number;
}

export interface ExecutionEvidence {
  kind: string;
  path: string | null;
  available: boolean;
  append_only: boolean;
  coverage: string;
  reason?: string | null;
  record_count?: number | null;
  ignored_record_count: number;
}

export interface ExecutionProgress {
  completed: number;
  finished_attempts?: number | null;
  total: number | null;
  determinate: boolean;
  reason?: string | null;
}

export interface ExecutionTaskAttempt {
  attempt_id: string;
  attempt_number: number | null;
  task_id?: string | null;
  task_hash?: string | null;
  native_id?: string | null;
  process: string;
  process_label: string;
  sample_or_shard?: string | null;
  state: string;
  exit_code?: number | null;
  submitted_at?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  duration?: string | null;
  realtime?: string | null;
  cpu?: string | null;
  peak_rss?: string | null;
  peak_vmem?: string | null;
  workdir?: string | null;
  container?: string | null;
}

export interface ExecutionProcess {
  name: string;
  label: string;
  counts: AttemptCounts;
}

export interface ExecutionObservation {
  schema_version: 1;
  engine: string;
  evidence: ExecutionEvidence;
  counts: AttemptCounts;
  count_unit: "task_attempts";
  progress: ExecutionProgress;
  structure: {
    kind: "discovered_processes";
    semantic_stages: false;
    ordering: string;
    processes: ExecutionProcess[];
  };
  attempts_truncated: boolean;
  attempts: ExecutionTaskAttempt[];
}

export interface RunDetail {
  binding: string;
  pipeline: Pipeline;
  workflow: string;
  target?: ComputeTargetRef;
  run_id: string;
  first_run_id: string;
  attempt_number: number;
  registry_run_id: string;
  revision: number;
  status: string;
  display_name?: string;
  analysis_summary?: string;
  failure_summary?: string | null;
  pid?: number;
  started_at_ms?: number | null;
  completed_at_ms?: number | null;
  run_dir: string;
  command_argv: string[];
  plan_checksum: string;
  profile?: string | null;
  workflow_revision?: string | null;
  workflow_source?: Record<string, unknown>;
  input_summary?: RunSummary["input_summary"];
  runtime_summary?: unknown;
  warnings: string[];
  returncode?: number | null;
}

export interface RunObservation {
  registry_run_id: string;
  revision: number;
  status: string;
  pid?: number | null;
  returncode?: number | null;
  failure_summary?: string | null;
  log_tail: string | null;
  execution: ExecutionObservation;
  warnings: string[];
}

export interface RunReport {
  registry_run_id: string;
  revision: number;
  availability: "available" | "not_completed" | "remote_results_not_projected" | "missing";
  report?: AnalysisReportData;
}

export interface RunSummary {
  registry_run_id: string;
  run_id: string;
  binding: string;
  pipeline: string;
  workflow: string;
  target?: ComputeTargetRef | null;
  status: string;
  display_name?: string;
  first_run_id: string;
  attempt_number: number;
  analysis_summary?: string;
  failure_summary?: string | null;
  profile?: string | null;
  workflow_revision?: string | null;
  input_summary?: {
    source: string;
    path?: string | null;
    sha256?: string | null;
    record_count?: number | null;
    sample_count?: number | null;
    read_layout?: string | null;
  } | null;
  runtime_summary?: unknown;
  revision: number;
  run_dir: string;
  pid: number | null;
  started_at_ms?: number | null;
  completed_at_ms?: number | null;
  returncode: number | null;
  created_at_ms?: number;
  updated_at_ms?: number;
}

export type DisplayMode = "inline" | "fullscreen";
