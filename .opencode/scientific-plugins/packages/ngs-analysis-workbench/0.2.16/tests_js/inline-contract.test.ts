import assert from "node:assert/strict";
import test from "node:test";

import { parseExecutionObservation } from "../src/execution-observation.ts";
import {
  mergeRunObservation,
  parseExecutionFailure,
  parsePlan,
  parseStartedRun,
} from "../src/inline/types.ts";

const checksum = `sha256:${"a".repeat(64)}`;
const planPayload = {
  ok: true,
  binding: "nextflow",
  plan_name: "FASTQ QC · public example",
  plan_id: "ngs-plan-0123456789abcdef",
  plan_checksum: checksum,
  runnable: true,
  request: {
    workflow: "nf-core/demo",
    profile: "test,docker",
    run_dir: "/workspace/ngs_runs/example",
    run_id: "nfcore-fastq-qc-example",
    target: { target_id: "local", provider: "ngs-analysis-workbench" },
  },
  command_argv: ["nextflow", "run", "nf-core/demo"],
  readiness: { ok: true, scope: "test", commands: [], blockers: [], warnings: [] },
  effects: {
    run_dir: "/workspace/ngs_runs/example",
    output_dir: "/workspace/results",
    work_dir: "/workspace/work",
    launch_log: "/workspace/ngs_runs/example/launch.log",
    local_writes: [],
    downloads: [],
    network_access: [],
  },
  preparation: {
    destination_dir: "/workspace/demo",
    download_bytes: 12_819_269,
    writes: ["/workspace/demo/inputs/sample1_R1.fastq.gz", "/workspace/demo/config.json"],
    operations: [
      {
        operation: "download_verified_file",
        relative_path: "inputs/sample1_R1.fastq.gz",
        path: "/workspace/demo/inputs/sample1_R1.fastq.gz",
        role: "SAMPLE1 read 1",
        url: "https://raw.githubusercontent.com/example/data.fastq.gz",
        bytes: 3_356_344,
        sha256: `sha256:${"d".repeat(64)}`,
      },
      {
        operation: "write_generated_file",
        relative_path: "config.json",
        path: "/workspace/demo/config.json",
        media_type: "application/json",
        content: "{}\n",
        bytes: 3,
        sha256: `sha256:${"e".repeat(64)}`,
      },
    ],
  },
  blockers: [],
  warnings: [],
  monitoring: {
    terminal_statuses: ["completed", "failed", "canceled", "orphaned"],
    log_paths: ["/workspace/demo/logs/nextflow.log"],
    artifact_paths: ["/workspace/demo/results"],
  },
};

const executionPayload = {
  schema_version: 1,
  engine: "nextflow",
  evidence: {
    kind: "nextflow_trace",
    path: "/run/workflow/trace.txt",
    available: true,
    append_only: true,
    coverage: "flushed task attempts",
    record_count: 1,
    ignored_record_count: 0,
  },
  counts: {
    total: 1,
    queued: 0,
    running: 0,
    completed: 1,
    cached: 0,
    failed: 0,
    aborted: 0,
    unknown: 0,
  },
  count_unit: "task_attempts",
  progress: {
    completed: 1,
    finished_attempts: 1,
    total: null,
    determinate: false,
    reason: "no planned denominator",
  },
  structure: {
    kind: "discovered_processes",
    semantic_stages: false,
    ordering: "first_terminal_observation",
    processes: [{
      name: "NFCORE:FASTQC",
      label: "FASTQC",
      counts: {
        total: 1,
        queued: 0,
        running: 0,
        completed: 1,
        cached: 0,
        failed: 0,
        aborted: 0,
        unknown: 0,
      },
    }],
  },
  attempts_truncated: true,
  attempts: [{
    attempt_id: "7",
    process: "NFCORE:FASTQC",
    process_label: "FASTQC",
    sample_or_shard: "S1",
    state: "completed",
  }],
};

const startedRunPayload = {
  ok: true,
  kind: "run",
  binding: "nextflow",
  registry_run_id: "ngs-run-0123456789abcdef",
  run_dir: "/workspace/ngs_runs/example",
  run_id: "nfcore-fastq-qc-example",
  status: "running",
  log_tail: "Waiting for tasks",
};

test("accepts a plan only when its native-approval identity is complete", () => {
  const plan = parsePlan(planPayload);

  assert.equal(plan?.planName, "FASTQ QC · public example");
  assert.equal(plan?.planId, "ngs-plan-0123456789abcdef");
  assert.equal(plan?.planChecksum, checksum);
  assert.equal(plan?.preparation?.downloadBytes, 12_819_269);
  assert.equal(plan?.preparation?.operations[0].operation, "download_verified_file");
});

test("preserves generic Nextflow engine identity in an approved plan", () => {
  const plan = parsePlan({ ...planPayload, binding: "nextflow" });
  assert.equal(plan?.binding, "nextflow");
});

test("preserves approved remote writes in the read-only plan review", () => {
  const plan = parsePlan({
    ...planPayload,
    effects: {
      ...planPayload.effects,
      remote_writes: ["/shared/ngs/run/results", "/shared/ngs/run/work"],
    },
  });

  assert.deepEqual(plan?.effects.remoteWrites, [
    "/shared/ngs/run/results",
    "/shared/ngs/run/work",
  ]);
});

test("rejects malformed remote effects instead of hiding them from plan review", () => {
  const plan = parsePlan({
    ...planPayload,
    effects: {
      ...planPayload.effects,
      remote_writes: [{ path: "/shared/ngs/run/hidden-result" }],
    },
  });

  assert.equal(plan, undefined);
});

test("rejects a malformed canonical plan checksum", () => {
  const plan = parsePlan({ ...planPayload, plan_checksum: "not-a-checksum" });

  assert.equal(plan, undefined);
});

test("rejects a plan without the explicit approval checksum", () => {
  const { plan_checksum: _planChecksum, ...incompletePlan } = planPayload;

  assert.equal(parsePlan(incompletePlan), undefined);
});

test("rejects malformed preparation instead of hiding it from plan review", () => {
  const malformed = {
    ...planPayload,
    preparation: {
      ...planPayload.preparation,
      operations: [{ operation: "shell_command", path: "/tmp/unsafe" }],
    },
  };

  assert.equal(parsePlan(malformed), undefined);
});

test("recognizes a rejected execution response without treating it as a rendering failure", () => {
  const failure = parseExecutionFailure({
    ok: false,
    errors: ["runtime snapshot is unknown to this server; call get_runtime_environment again"],
  });

  assert.equal(
    failure?.message,
    "runtime snapshot is unknown to this server; call get_runtime_environment again",
  );
  assert.equal(
    failure?.recovery,
    "Refresh the runtime environment, then create and review a new execution plan.",
  );
});

test("preserves non-snapshot execution errors without inventing a recovery action", () => {
  const failure = parseExecutionFailure({
    ok: false,
    errors: ["approved plan checksum does not match", "execution was not started"],
  });

  assert.equal(failure?.message, "approved plan checksum does not match\nexecution was not started");
  assert.equal(failure?.recovery, undefined);
});

test("keeps malformed error payloads on the invalid-response path", () => {
  assert.equal(parseExecutionFailure({ ok: false, errors: [] }), undefined);
  assert.equal(parseExecutionFailure({ ok: false, errors: [42] }), undefined);
  assert.equal(parseExecutionFailure({ ok: true, errors: ["not a failed response"] }), undefined);
});

test("requires a durable registry identity for a started run receipt", () => {
  const run = parseStartedRun(startedRunPayload, undefined);
  const { registry_run_id: _registryRunId, ...incompleteRun } = startedRunPayload;

  assert.equal(run?.registryRunId, "ngs-run-0123456789abcdef");
  assert.equal(parseStartedRun(incompleteRun, undefined), undefined);
});

test("requires a discovered run to match the reviewed plan checksum", () => {
  const plan = parsePlan(planPayload);
  assert.ok(plan);

  assert.equal(parseStartedRun({
    ...startedRunPayload,
    plan_checksum: checksum,
  }, undefined, plan)?.registryRunId, "ngs-run-0123456789abcdef");
  assert.equal(parseStartedRun({
    ...startedRunPayload,
    plan_checksum: `sha256:${"b".repeat(64)}`,
  }, undefined, plan), undefined);
});

test("merges polled log and trace evidence into the approved run receipt", () => {
  const run = parseStartedRun(startedRunPayload, undefined);
  assert.ok(run);

  const refreshed = mergeRunObservation(run, {
    ok: true,
    registry_run_id: run.registryRunId,
    revision: 3,
    status: "completed",
    returncode: 0,
    log_tail: "Workflow completed",
    execution: executionPayload,
  });

  assert.equal(refreshed.status, "completed");
  assert.equal(refreshed.returncode, 0);
  assert.equal(refreshed.logTail, "Workflow completed");
  assert.equal(refreshed.execution?.evidence.kind, "nextflow_trace");
  assert.equal(refreshed.execution?.attempts[0].process_label, "FASTQC");
});

test("ignores stale observations and clears an unavailable log tail", () => {
  const run = parseStartedRun({ ...startedRunPayload, revision: 2 }, undefined);
  assert.ok(run);
  const completed = mergeRunObservation(run, {
    ok: true,
    registry_run_id: run.registryRunId,
    revision: 3,
    status: "completed",
    log_tail: null,
    failure_summary: "Controller exited before completion.",
    execution: executionPayload,
  });
  const stale = mergeRunObservation(completed, {
    ok: true,
    registry_run_id: run.registryRunId,
    revision: 2,
    status: "running",
    log_tail: "stale output",
    execution: executionPayload,
  });

  assert.equal(completed.logTail, null);
  assert.equal(completed.failureSummary, "Controller exited before completion.");
  assert.equal(stale, completed);
});

test("rejects a status response for a different durable run", () => {
  const run = parseStartedRun(startedRunPayload, undefined);
  assert.ok(run);

  assert.throws(
    () => mergeRunObservation(run, {
      ok: true,
      registry_run_id: "ngs-run-different",
    }),
    /did not match the approved run receipt/,
  );
});

test("normalizes a typed execution observation from an MCP payload", () => {
  const execution = parseExecutionObservation(executionPayload);

  assert.equal(execution?.evidence.kind, "nextflow_trace");
  assert.equal(execution?.progress.total, null);
  assert.equal(execution?.attempts_truncated, true);
  assert.equal(execution?.attempts[0].attempt_number, null);
});

test("rejects an execution observation with a malformed attempt", () => {
  const execution = parseExecutionObservation({
    schema_version: 1,
    engine: "nextflow",
    evidence: {},
    counts: {},
    progress: {},
    structure: { processes: [] },
    attempts: [{ attempt_id: 7 }],
  });

  assert.equal(execution, undefined);
});
