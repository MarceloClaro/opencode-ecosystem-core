import type {
  AttemptCounts,
  ExecutionObservation,
  ExecutionTaskAttempt,
} from "../model";

const emptyCounts: AttemptCounts = {
  total: 0,
  queued: 0,
  running: 0,
  completed: 0,
  cached: 0,
  failed: 0,
  aborted: 0,
  unknown: 0,
};

function counts(overrides: Partial<AttemptCounts>): AttemptCounts {
  return { ...emptyCounts, ...overrides };
}

function attempt(
  attemptId: string,
  process: string,
  sampleOrShard: string,
  state: string,
  duration?: string,
  peakRss?: string,
): ExecutionTaskAttempt {
  return {
    attempt_id: attemptId,
    attempt_number: 1,
    process,
    process_label: process.split(":").at(-1) ?? process,
    sample_or_shard: sampleOrShard,
    state,
    duration: duration ?? null,
    peak_rss: peakRss ?? null,
  };
}

const nextflowAttempts = [
  attempt("1", "NFCORE_RNASEQ:RNASEQ:VALIDATE_INPUTS", "8 samples", "completed", "1m"),
  attempt("2", "NFCORE_RNASEQ:RNASEQ:FASTQC", "PBMC_01", "completed", "7m", "3.2 GB"),
  attempt("3", "NFCORE_RNASEQ:RNASEQ:TRIMGALORE", "PBMC_01", "completed", "14m", "2.1 GB"),
  attempt("4", "NFCORE_RNASEQ:RNASEQ:ALIGN_STAR:STAR_ALIGN", "PBMC_04", "completed", "23m", "46.8 GB"),
  attempt("5", "NFCORE_RNASEQ:RNASEQ:QUANTIFY_STAR_SALMON:SALMON_QUANT", "PBMC_06", "completed", "8m", "28.1 GB"),
  attempt("6", "NFCORE_RNASEQ:RNASEQ:QUANTIFY_STAR_SALMON:SALMON_QUANT", "PBMC_07", "completed", "7m", "25.4 GB"),
];

export const nextflowTraceObservation: ExecutionObservation = {
  schema_version: 1,
  engine: "nextflow",
  evidence: {
    kind: "nextflow_trace",
    path: "/workspaces/lung-rnaseq/ngs_runs/nextflow/rnaseq/run/workflow/trace.txt",
    available: true,
    append_only: true,
    coverage: "flushed task attempts",
    record_count: nextflowAttempts.length,
    ignored_record_count: 0,
  },
  counts: counts({ total: nextflowAttempts.length, completed: nextflowAttempts.length }),
  count_unit: "task_attempts",
  progress: {
    completed: nextflowAttempts.length,
    finished_attempts: nextflowAttempts.length,
    total: null,
    determinate: false,
    reason: "the trace contains observed attempts, not a planned task denominator",
  },
  structure: {
    kind: "discovered_processes",
    semantic_stages: false,
    ordering: "first_terminal_observation",
    processes: [
      { name: nextflowAttempts[0].process, label: "VALIDATE_INPUTS", counts: counts({ total: 1, completed: 1 }) },
      { name: nextflowAttempts[1].process, label: "FASTQC", counts: counts({ total: 1, completed: 1 }) },
      { name: nextflowAttempts[2].process, label: "TRIMGALORE", counts: counts({ total: 1, completed: 1 }) },
      { name: nextflowAttempts[3].process, label: "STAR_ALIGN", counts: counts({ total: 1, completed: 1 }) },
      { name: nextflowAttempts[4].process, label: "SALMON_QUANT", counts: counts({ total: 2, completed: 2 }) },
    ],
  },
  attempts_truncated: false,
  attempts: nextflowAttempts,
};

const snakemakeAttempts = [
  attempt("1:1", "stage_fastq", "sample=S10", "completed", "2s"),
  attempt("2:1", "fastqc", "sample=S10, read=R1", "running"),
];

export const snakemakeLogObservation: ExecutionObservation = {
  schema_version: 1,
  engine: "snakemake",
  evidence: {
    kind: "snakemake_native_log",
    path: "/tmp/test-qc/ngs_runs/snakemake/fastq_qc/run/.snakemake/log/2026.snakemake.log",
    available: true,
    append_only: true,
    coverage: "native Snakemake execution log",
    record_count: 42,
    ignored_record_count: 0,
  },
  counts: counts({ total: 2, completed: 1, running: 1 }),
  count_unit: "task_attempts",
  progress: { completed: 1, total: 3, determinate: true },
  structure: {
    kind: "discovered_processes",
    semantic_stages: false,
    ordering: "first_runtime_observation",
    processes: [
      { name: "stage_fastq", label: "stage_fastq", counts: counts({ total: 1, completed: 1 }) },
      { name: "fastqc", label: "fastqc", counts: counts({ total: 1, running: 1 }) },
    ],
  },
  attempts_truncated: false,
  attempts: snakemakeAttempts,
};
