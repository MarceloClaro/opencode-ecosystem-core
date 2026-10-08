import assert from "node:assert/strict";
import test from "node:test";

import {
  isActiveRunStatus,
  isTerminalRunStatus,
  latestActiveRunFilters,
  runStatusPresentation,
} from "../src/runStatus.ts";

test("queries the latest active run without restricting the workflow engine", () => {
  assert.deepEqual(latestActiveRunFilters(), {
    statuses: ["starting", "running", "cancel_requested", "canceling"],
    limit: 1,
  });
});

test("recognizes only statuses that require active monitoring", () => {
  for (const status of [
    "starting",
    "running",
    "cancel_requested",
    "canceling",
  ]) {
    assert.equal(isActiveRunStatus(status), true, status);
  }
  for (const status of [
    "completed",
    "failed",
    "canceled",
    "orphaned",
    undefined,
  ]) {
    assert.equal(isActiveRunStatus(status), false, status);
  }
});

test("recognizes terminal workflow statuses", () => {
  for (const status of ["completed", "failed", "canceled", "orphaned"]) {
    assert.equal(isTerminalRunStatus(status), true, status);
  }
  for (const status of [
    "starting",
    "running",
    "cancel_requested",
    "canceling",
    "unknown",
  ]) {
    assert.equal(isTerminalRunStatus(status), false, status);
  }
});

test("centralizes visible status labels and tones", () => {
  assert.deepEqual(runStatusPresentation("completed"), {
    label: "Completed",
    status: "completed",
    tone: "success",
  });
  assert.deepEqual(runStatusPresentation("orphaned"), {
    label: "Orphaned",
    status: "orphaned",
    tone: "warning",
  });
  assert.deepEqual(runStatusPresentation("running"), {
    label: "Running",
    status: "running",
    tone: "info",
  });
  assert.deepEqual(runStatusPresentation("finished_unverified"), {
    label: "Finished unverified",
    status: "finished_unverified",
    tone: "neutral",
  });
});
