import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import {
  analysisSummaryMessage,
  HISTORY_SUMMARY_CHARACTER_LIMIT,
  plainTextAnalysisSummary,
  runHistorySummary,
} from "../src/analysisSummary.ts";

test("keeps a durable analysis visible while the local report loads or fails", () => {
  const summary = "FastQC completed with no adapter warning.";
  assert.equal(analysisSummaryMessage(summary, true), summary);
  assert.equal(analysisSummaryMessage(summary, false, "Report unavailable"), summary);
  assert.equal(
    analysisSummaryMessage(undefined, true),
    "Run information is ready; loading the completed report.",
  );
  assert.equal(analysisSummaryMessage(undefined, false, "Report unavailable"), "Report unavailable");
});

test("renders scientific summaries as one plain-text paragraph", () => {
  const summary = plainTextAnalysisSummary(
    "Paired *Allobates femoralis* RNA-seq reads passed **FastQC**.\n" +
      "Review [MultiQC](https://example.test/report) and `R1` duplication.",
  );

  assert.match(summary, /Allobates femoralis/);
  assert.match(summary, /FastQC/);
  assert.match(summary, /MultiQC/);
  assert.match(summary, /R1 duplication/);
  assert.doesNotMatch(summary, /[*`\n]/);
  assert.doesNotMatch(summary, /https:\/\//);
});

test("caps a complete plain-text run-history sentence at 125 characters without an ellipsis", () => {
  const summary = "*scientifically relevant detail* ".repeat(10);
  const preview = runHistorySummary(summary);

  assert.equal(HISTORY_SUMMARY_CHARACTER_LIMIT, 125);
  assert.ok(preview.length <= 125);
  assert.equal(preview.endsWith("."), true);
  assert.doesNotMatch(preview, /(?:…|\.\.\.)/);
  assert.doesNotMatch(preview, /\*/);
});

test("shows only the complete contextual first sentence in run history", () => {
  const summary = runHistorySummary(
    "FastQC on public Pincho-paper sample SRR8288062 from *Allobates femoralis* skin RNA-seq. " +
      "Both original mates contain 3,494,637 reads and pass base-quality review.",
  );

  assert.match(summary, /FastQC/);
  assert.match(summary, /Allobates femoralis/);
  assert.doesNotMatch(summary, /Both original mates/);
  assert.doesNotMatch(summary, /\*/);
  assert.match(summary, /[.!?]$/);
});

test("removes ellipses from older run-history previews", () => {
  const summary = runHistorySummary(
    "FastQC on a public paired-end RNA-seq sample…",
  );

  assert.doesNotMatch(summary, /(?:…|\.\.\.)/);
  assert.match(summary, /[.!?]$/);
});

test("run-history summary styling does not introduce a visual ellipsis", () => {
  const stylesheet = readFileSync(
    new URL("../src/components/RunHistory.module.css", import.meta.url),
    "utf8",
  );

  assert.match(stylesheet, /\.historySummary\s*\{[^}]*text-overflow:\s*clip;/s);
});

test("keeps short run-history summaries untruncated", () => {
  const summary = runHistorySummary(
    "**FastQC** completed; no adapter trimming is justified.",
  );

  assert.match(summary, /FastQC/);
  assert.match(summary, /no adapter trimming/);
  assert.doesNotMatch(summary, /\*/);
  assert.match(summary, /[.!?]$/);
});
