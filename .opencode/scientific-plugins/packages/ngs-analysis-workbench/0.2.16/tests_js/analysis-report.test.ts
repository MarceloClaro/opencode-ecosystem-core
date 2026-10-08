import assert from "node:assert/strict";
import test from "node:test";

import { parseAnalysisReport } from "../src/report/parse.ts";

test("normalizes the completed-run report returned by MCP", () => {
  const payload = {
    schema_version: 1,
    title: "Bulk RNA-seq results",
    description: "Counts and quality review.",
    summary:
      "For the lung-cohort comparison, six samples support downstream quantification.\nOne sample needs duplication review.",
    completed_at_ms: Date.UTC(2026, 7, 7, 9, 42),
    duration_ms: 872_000,
    run_directory: "/workspace/ngs_runs/snakemake/rnaseq/run-one",
    artifact_count: 24,
    artifact_count_truncated: false,
    metrics: [{ label: "Status", value: "Completed", tone: "success" }],
    warnings: ["Review one sample."],
    entries: [
      {
        id: "multiqc",
        title: "MultiQC",
        path: "reports/multiqc.html",
        open_url: "http://127.0.0.1:8765/reports/multiqc.html",
        kind: "localhost_app",
        status: "created",
        description: "Quality report.",
        size_bytes: 1_048_576,
      },
    ],
    notes: ["Inputs remained read-only."],
    provenance: [{ label: "Workflow", value: "nf-core/rnaseq" }],
    sources: [
      { label: "Scientific analysis", path: "analysis_summary.md" },
      { label: "Artifact index", path: "artifact_index.json" },
    ],
  };
  const result = parseAnalysisReport(payload);

  assert.equal(result?.title, "Bulk RNA-seq results");
  assert.match(result?.completedAt ?? "", /2026/);
  assert.equal(result?.duration, "14 min 32 sec");
  assert.match(result?.summary ?? "", /lung-cohort comparison/);
  assert.match(result?.summary ?? "", /duplication review/);
  assert.equal(result?.entries[0].size, "1.0 MB");
  assert.equal(
    result?.entries[0].openUrl,
    "http://127.0.0.1:8765/reports/multiqc.html",
  );
  assert.deepEqual(result?.sources, [
    { label: "Scientific analysis", path: "analysis_summary.md" },
    { label: "Artifact index", path: "artifact_index.json" },
  ]);

  const pending = parseAnalysisReport({ ...payload, summary: "" });
  assert.equal(pending?.summary, "");
  assert.deepEqual(pending?.entries, result?.entries);
  assert.deepEqual(pending?.sources, result?.sources);
});

test("rejects an incomplete result contract instead of rendering invented data", () => {
  assert.equal(
    parseAnalysisReport({
      schema_version: 1,
      title: "Missing run directory",
      description: "Incomplete payload.",
      summary: "No directory.",
      artifact_count: 0,
    }),
    undefined,
  );
});
