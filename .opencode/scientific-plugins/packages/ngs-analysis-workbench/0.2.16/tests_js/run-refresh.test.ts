import assert from "node:assert/strict";
import test from "node:test";

import type { RunSummary } from "../src/model.ts";
import { isCurrentObservation, mergeRunIntoHistory } from "../src/runRefresh.ts";

test("rejects observations for another run or an older revision", () => {
  const identity = { registryRunId: "registry-current", revision: 4 };
  assert.equal(isCurrentObservation(identity, {
    registry_run_id: "registry-other",
    revision: 5,
  }), false);
  assert.equal(isCurrentObservation(identity, {
    registry_run_id: "registry-current",
    revision: 3,
  }), false);
  assert.equal(isCurrentObservation(identity, {
    registry_run_id: "registry-current",
    revision: 4,
  }), true);
});

test("patches a refreshed detail run into durable history without remapping unrelated rows", () => {
  const target = runSummary({
    registry_run_id: "registry-target",
    pid: 1234,
    revision: 1,
    status: "running",
  });
  const other = runSummary({
    registry_run_id: "registry-other",
    revision: 7,
    status: "completed",
  });

  const [patched, untouched] = mergeRunIntoHistory([target, other], {
    registry_run_id: "registry-target",
    revision: 2,
    status: "failed",
    returncode: 1,
  });

  assert.equal(untouched, other);
  assert.deepEqual(
    {
      pid: patched?.pid,
      returncode: patched?.returncode,
      revision: patched?.revision,
      status: patched?.status,
    },
    {
      pid: null,
      returncode: 1,
      revision: 2,
      status: "failed",
    },
  );
});

function runSummary(overrides: Partial<RunSummary> = {}): RunSummary {
  return {
    binding: "nextflow",
    pipeline: "fastq_qc",
    registry_run_id: "registry-run",
    revision: 1,
    run_dir: "/workspaces/ngs/ngs_runs/nextflow/fastq_qc/run",
    run_id: "run",
    status: "running",
    workflow: "nf-core/demo",
    pid: null,
    returncode: null,
    ...overrides,
  };
}
