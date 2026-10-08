from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
MCP_ROOT = PLUGIN_ROOT / "mcp"
if str(MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(MCP_ROOT))

from ngs_workbench_mcp.report import (  # noqa: E402
    analysis_summary_review,
    analysis_summary_takeaway,
    build_completed_report,
)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


class AnalysisReportTests(unittest.TestCase):
    def test_prefers_contextual_scientific_summary_without_replacing_workflow_title(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            run_dir = workspace / "ngs_runs" / "snakemake" / "fastq_qc" / "run-context"
            run_dir.mkdir(parents=True)
            (run_dir / "summary.md").write_text(
                "# Paired-end RNA-seq quality control\n\nWorkflow completed.\n",
                encoding="utf-8",
            )
            (run_dir / "analysis_summary.md").write_text(
                "# Scientific analysis summary\n\n"
                "For the planned *lung inflammation* comparison, paired **RNA-seq** "
                "reads were assessed. Six libraries completed FastQC and MultiQC. "
                "Observed read depth supports downstream quantification. "
                "Elevated R1 duplication warrants review. "
                "Differential expression and biological findings are not established. "
                "Review library complexity before expression quantification. "
                "This seventh sentence must not appear in the visible summary.\n\n"
                "## Scientific context and question\n"
                "Study: lung inflammation comparison.\n"
                "Experimental unit: six RNA-seq libraries.\n"
                "Durable registry run: b582a20d-f87e-4893-98b4-c1e5700e623f.\n"
                "Approved plan checksum: sha256:" + "a" * 64 + "\n"
                "## Key findings\n"
                "Read depth: 3,494,637 read pairs.\n"
                "GC content: 44%.\n"
                "Adapters: not detected.\n"
                "R1 duplication: 34.1%.\n"
                "R2 duplication: 15.2%.\n"
                "## Recommended next step\n"
                "Review library complexity before expression quantification.\n",
                encoding="utf-8",
            )

            result = build_completed_report(
                run_dir,
                workspace_dir=workspace,
                run_id="run-context",
                binding="snakemake",
                pipeline="fastq_qc",
                workflow="bundled/fastq_qc",
                display_name="Lung study QC",
                status="completed",
                started_at_ms=None,
                completed_at_ms=None,
            )

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["title"], "Paired-end RNA-seq quality control")
        self.assertIn("planned lung inflammation comparison", result["summary"])
        self.assertIn("Review library complexity", result["summary"])
        self.assertEqual(result["summary"].count("."), 6)
        for technical in (
            "*",
            "Study:",
            "Experimental unit:",
            "Durable registry run:",
            "sha256:",
            "R2 duplication: 15.2%",
            "seventh sentence",
        ):
            with self.subTest(technical=technical):
                self.assertNotIn(technical, result["summary"])
        self.assertNotIn("Workflow completed.", result["summary"])
        self.assertEqual(
            result["sources"],
            [
                {"label": "Scientific analysis", "path": "analysis_summary.md"},
                {"label": "Summary", "path": "summary.md"},
            ],
        )

    def test_history_takeaway_uses_one_complete_bounded_scientific_sentence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            run_dir = workspace / "ngs_runs" / "nextflow" / "rnaseq" / "run-takeaway"
            run_dir.mkdir(parents=True)
            (run_dir / "analysis_summary.md").write_text(
                "# Scientific analysis summary\n\n"
                "For treatment-response study, six *RNA-seq* libraries support\n"
                "downstream quantification; one sample needs **duplication review**.\n\n"
                "## Limitations\n"
                "Differential expression has not been performed.\n",
                encoding="utf-8",
            )

            takeaway = analysis_summary_takeaway(run_dir, workspace_dir=workspace)

            (run_dir / "analysis_summary.md").write_text(
                "# Scientific analysis summary\n\n" + "x" * 400,
                encoding="utf-8",
            )
            truncated = analysis_summary_takeaway(run_dir, workspace_dir=workspace)

        self.assertEqual(
            takeaway,
            "For treatment-response study, six RNA-seq libraries support "
            "downstream quantification; one sample needs duplication review.",
        )
        self.assertNotIn("Differential expression", takeaway)
        self.assertNotIn("*", takeaway)
        self.assertEqual(len(truncated), 125)
        self.assertTrue(truncated.endswith("."))
        self.assertNotIn("…", truncated)

    def test_history_uses_dedicated_takeaway_without_rewriting_detail_sentence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            run_dir = workspace / "ngs_runs" / "snakemake" / "fastq_qc" / "run-pincho"
            run_dir.mkdir(parents=True)
            expected = (
                "FastQC of Allobates femoralis skin RNA-seq sample SRR8288062; "
                "high-quality reads, no trimming needed."
            )
            detail = (
                "This analysis assessed whether public paired-end skin RNA-sequencing "
                "reads from Allobates femoralis discussed in the Pincho transcriptomics "
                "paper are suitable for downstream analysis. "
                "FastQC and MultiQC completed successfully. "
                "Each original mate contained 3,494,637 high-quality reads. "
                "Negligible adapter signal does not justify trimming. "
                "Read QC cannot establish expression differences or biological findings. "
                "Continue downstream transcriptome analysis without trimming."
            )
            (run_dir / "analysis_summary.md").write_text(
                f"# Scientific analysis summary\n\nTakeaway: {expected}\n\n{detail}\n",
                encoding="utf-8",
            )

            takeaway = analysis_summary_takeaway(
                run_dir,
                workspace_dir=workspace,
                pipeline="fastq_qc",
                status="completed",
            )
            review = analysis_summary_review(run_dir, workspace_dir=workspace)

        self.assertEqual(takeaway, expected)
        self.assertEqual(review, detail)
        self.assertEqual(review.count("."), 6)
        self.assertIn("3,494,637 high-quality reads", review)
        self.assertIn("biological findings", review)
        self.assertIn("without trimming", review)
        self.assertNotIn("Takeaway:", review)
        self.assertNotIn("fastqc on this analysis", takeaway.lower())
        self.assertLessEqual(len(takeaway), 125)

    def test_short_history_takeaways_preserve_noncompleted_run_states(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            run_dir = workspace / "ngs_runs" / "snakemake" / "fastq_qc" / "run-status"
            run_dir.mkdir(parents=True)
            (run_dir / "analysis_summary.md").write_text(
                "Takeaway: FastQC of sample SRR8288062; final read quality is unavailable.\n\n"
                "This run has not completed and does not support final QC conclusions.\n",
                encoding="utf-8",
            )

            for status, label in (
                ("starting", "Starting"),
                ("running", "Running"),
                ("failed", "Failed"),
                ("blocked", "Blocked"),
                ("cancel_requested", "Canceling"),
                ("canceled", "Canceled"),
                ("orphaned", "Orphaned"),
                ("finished_unverified", "Unverified"),
            ):
                with self.subTest(status=status):
                    takeaway = analysis_summary_takeaway(
                        run_dir,
                        workspace_dir=workspace,
                        pipeline="fastq_qc",
                        status=status,
                    )
                    self.assertTrue(takeaway.startswith(f"{label}:"))
                    self.assertLessEqual(len(takeaway), 125)

            (run_dir / "analysis_summary.md").write_text(
                "Takeaway: Running: FastQC of SRR8288062; final read quality is pending.\n\n"
                "Final read quality cannot yet be established.\n",
                encoding="utf-8",
            )
            already_labeled = analysis_summary_takeaway(
                run_dir,
                workspace_dir=workspace,
                status="running",
            )

        self.assertEqual(
            already_labeled,
            "Running: FastQC of SRR8288062; final read quality is pending.",
        )

    def test_history_takeaway_replaces_a_stale_lifecycle_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            run_dir = workspace / "ngs_runs" / "snakemake" / "fastq_qc" / "run-status"
            run_dir.mkdir(parents=True)
            (run_dir / "analysis_summary.md").write_text(
                "Takeaway: Running: FastQC completed; Salmon is still pending.\n",
                encoding="utf-8",
            )

            takeaways = {
                status: analysis_summary_takeaway(
                    run_dir,
                    workspace_dir=workspace,
                    status=status,
                )
                for status in ("running", "completed", "failed")
            }

        self.assertEqual(
            takeaways["running"],
            "Running: FastQC completed; Salmon is still pending.",
        )
        self.assertEqual(takeaways["completed"], "FastQC completed; Salmon is still pending.")
        self.assertEqual(
            takeaways["failed"],
            "Failed: FastQC completed; Salmon is still pending.",
        )

    def test_history_takeaway_uses_registry_fallback_when_review_has_no_narrative(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            run_dir = workspace / "ngs_runs" / "snakemake" / "rnaseq" / "run-failed"
            run_dir.mkdir(parents=True)
            (run_dir / "analysis_summary.md").write_text(
                "# Scientific analysis summary\n\n| Metric | Value |\n| --- | --- |\n",
                encoding="utf-8",
            )

            takeaway = analysis_summary_takeaway(
                run_dir,
                workspace_dir=workspace,
                fallback=(
                    "Salmon quantification failed because the transcriptome index is missing. "
                    "Gene-level conclusions are unsupported."
                ),
                pipeline="rnaseq",
                status="failed",
            )
            report = build_completed_report(
                run_dir,
                workspace_dir=workspace,
                run_id="run-failed",
                binding="snakemake",
                pipeline="rnaseq",
                workflow="bundled/rnaseq",
                display_name="Failed quantification",
                status="completed",
                started_at_ms=None,
                completed_at_ms=1_000,
            )

        self.assertEqual(
            takeaway,
            "Failed: Salmon quantification failed because the transcriptome index is missing.",
        )
        self.assertIsNotNone(report)
        assert report is not None
        self.assertEqual(report["summary"], "")
        self.assertIn(
            {"label": "Scientific analysis", "path": "analysis_summary.md"},
            report["sources"],
        )

    def test_history_takeaway_condenses_existing_long_sample_context(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            run_dir = workspace / "ngs_runs" / "snakemake" / "fastq_qc" / "run-pincho"
            run_dir.mkdir(parents=True)
            (run_dir / "analysis_summary.md").write_text(
                "# Scientific analysis summary\n\n"
                "The public Pincho-paper sample SRR8288062, identified in existing "
                "verified dataset metadata as *Allobates femoralis* skin RNA-seq, "
                "completed native paired-end FastQC and MultiQC analysis successfully. "
                "Both original mates show high per-base quality.\n",
                encoding="utf-8",
            )

            takeaway = analysis_summary_takeaway(
                run_dir,
                workspace_dir=workspace,
                pipeline="fastq_qc",
                status="completed",
            )
            review = analysis_summary_review(run_dir, workspace_dir=workspace)

        self.assertEqual(
            takeaway,
            "FastQC on public Pincho-paper sample SRR8288062 from "
            "Allobates femoralis skin RNA-seq.",
        )
        self.assertLessEqual(len(takeaway), 100)
        self.assertNotIn("…", takeaway)
        self.assertIn("Both original mates show high per-base quality.", review)

    def test_reads_noncomplete_scientific_reviews_without_claiming_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            run_dir = workspace / "ngs_runs" / "snakemake" / "rnaseq" / "run-failed"
            (run_dir / "fastqc").mkdir(parents=True)
            (run_dir / "fastqc" / "sample_fastqc.html").write_text(
                "<html>partial read QC</html>",
                encoding="utf-8",
            )
            (run_dir / "analysis_summary.md").write_text(
                "# Scientific analysis summary\n\n"
                "The inflammation study stopped after FastQC; Salmon quantification "
                "failed because its reference index is missing. "
                "Differential expression and biological conclusions are unsupported.\n\n"
                "## Limitations\n"
                "Plan ID: 6f95526a-ec50-44f5-82af-f436c9b9f1fd.\n",
                encoding="utf-8",
            )

            review = analysis_summary_review(run_dir, workspace_dir=workspace)

        self.assertIn("stopped after FastQC", review)
        self.assertIn("biological conclusions are unsupported", review)
        self.assertNotIn("Plan ID", review)

    def test_history_takeaway_uses_registry_evidence_without_a_run_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            missing_run_dir = workspace / "ngs_runs" / "snakemake" / "rnaseq" / "missing"
            fallback = (
                "Lung treatment comparison: execution is blocked because the approved "
                "workspace is unavailable. No workflow stages or biological findings "
                "can be verified."
            )

            takeaway = analysis_summary_takeaway(
                missing_run_dir,
                workspace_dir=workspace,
                fallback=fallback,
            )

        self.assertEqual(
            takeaway,
            "Lung treatment comparison: execution is blocked because the "
            "approved workspace is unavailable.",
        )
        self.assertLessEqual(len(takeaway), 125)
        self.assertNotIn("…", takeaway)
        self.assertFalse(missing_run_dir.exists())

    def test_long_failed_history_takeaway_preserves_status_without_an_ellipsis(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            missing_run_dir = workspace / "ngs_runs" / "snakemake" / "rnaseq" / "missing"
            fallback = (
                "The treated peripheral-blood immune-response study involving multiple "
                "independent patient cohorts failed because the approved reference index "
                "is unavailable. Biological conclusions cannot be supported."
            )

            takeaway = analysis_summary_takeaway(
                missing_run_dir,
                workspace_dir=workspace,
                fallback=fallback,
                pipeline="rnaseq",
                status="failed",
            )

        self.assertTrue(takeaway.startswith("Failed: Bulk RNA-seq on"))
        self.assertIn("the approved reference index is unavailable", takeaway)
        self.assertTrue(takeaway.endswith("."))
        self.assertLessEqual(len(takeaway), 125)
        self.assertNotIn("…", takeaway)

    def test_visible_scientific_summary_uses_opening_narrative_paragraph(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            run_dir = workspace / "ngs_runs" / "snakemake" / "fastq_qc" / "run-clean"
            run_dir.mkdir(parents=True)
            (run_dir / "analysis_summary.md").write_text(
                "# Scientific analysis summary\n\n"
                "Paired *Allobates femoralis* skin RNA-seq reads were assessed. "
                "Both mates contain 3,494,637 reads. "
                "Base quality is strong and adapter signal is negligible. "
                "Composition and duplication flags do not justify trimming. "
                "Read QC alone cannot establish a biological finding. "
                "Continue to the planned transcriptome analysis without trimming. "
                "This seventh sentence must not appear in the visible summary.\n"
                "| Metric | R1 | R2 |\n"
                "| --- | ---: | ---: |\n",
                encoding="utf-8",
            )

            summary = analysis_summary_review(run_dir, workspace_dir=workspace)
            preview = analysis_summary_takeaway(run_dir, workspace_dir=workspace)

        self.assertIn("Allobates femoralis", summary)
        self.assertIn("Continue to the planned transcriptome analysis", summary)
        self.assertEqual(summary.count("."), 6)
        self.assertLessEqual(len(preview), 125)
        for technical in ("*", "| Metric |", "seventh sentence"):
            with self.subTest(technical=technical):
                self.assertNotIn(technical, summary)
                self.assertNotIn(technical, preview)

    def test_projects_standard_manifests_into_a_bounded_result(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            run_dir = workspace / "ngs_runs" / "snakemake" / "rnaseq" / "run-one"
            run_dir.mkdir(parents=True)
            (run_dir / "summary.md").write_text(
                "# Bulk RNA-seq summary\n\nStatus: `completed`\n\nSamples parsed: `6`\n",
                encoding="utf-8",
            )
            (run_dir / "tables").mkdir()
            (run_dir / "tables" / "counts.tsv").write_text("gene\tsample\n", encoding="utf-8")
            (run_dir / "reports").mkdir()
            (run_dir / "reports" / "multiqc.html").write_text("<html></html>", encoding="utf-8")
            write_json(
                run_dir / "run_manifest.json",
                {
                    "schema_version": "0.4.0",
                    "workflow": "local_light_snakemake_salmon",
                    "audit": {"parameter_sha256": "abc123"},
                },
            )
            write_json(
                run_dir / "artifact_index.json",
                {
                    "artifacts": [
                        {"path": "tables/counts.tsv", "bytes": 128},
                        {"path": "reports/multiqc.html", "bytes": 256},
                        {"path": "../outside.txt", "bytes": 512},
                    ]
                },
            )
            write_json(
                run_dir / "visualizations" / "visualization_manifest.json",
                {
                    "title": "Bulk RNA-seq Counts/QC Review Bundle",
                    "description": "Review the generated matrices and quality reports.",
                    "entries": [
                        {
                            "id": "live-report",
                            "title": "Live MultiQC",
                            "path": "http://127.0.0.1:8765/reports/multiqc.html",
                            "kind": "localhost_app",
                            "status": "created",
                            "description": "Locally served report.",
                        },
                        {
                            "id": "counts",
                            "title": "Counts",
                            "path": "tables/counts.tsv",
                            "kind": "table",
                            "status": "created",
                            "description": "Gene counts.",
                        },
                        {
                            "id": "unsafe",
                            "title": "Unsafe path",
                            "path": "../../outside.txt",
                            "kind": "text",
                            "status": "created",
                            "description": "Must not be exposed.",
                        },
                    ],
                    "notes": ["Review MultiQC before differential expression."],
                },
            )
            write_json(run_dir / "qc" / "qc_verdict.json", {"overall_status": "review"})

            result = build_completed_report(
                run_dir,
                workspace_dir=workspace,
                run_id="run-one",
                binding="snakemake",
                pipeline="rnaseq",
                workflow="bundled/rnaseq",
                display_name="Lung cohort",
                status="completed",
                started_at_ms=1_000,
                completed_at_ms=61_000,
            )

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["title"], "Bulk RNA-seq Counts/QC Review Bundle")
        self.assertEqual(result["artifact_count"], 2)
        self.assertEqual(result["duration_ms"], 60_000)
        self.assertEqual(result["summary"], "")
        self.assertEqual(
            result["warnings"],
            ["QC verdict is Review; review qc/qc_verdict.json before downstream analysis."],
        )
        self.assertEqual(
            next(entry for entry in result["entries"] if entry["id"] == "live-report")["open_url"],
            "http://127.0.0.1:8765/reports/multiqc.html",
        )
        unsafe = next(entry for entry in result["entries"] if entry["id"] == "unsafe")
        self.assertIsNone(unsafe["path"])
        self.assertEqual(unsafe["status"], "not_available")
        self.assertEqual(
            [source["path"] for source in result["sources"]],
            [
                "summary.md",
                "run_manifest.json",
                "visualizations/visualization_manifest.json",
                "artifact_index.json",
            ],
        )

    def test_projects_results_root_manifests_without_trusting_workflow_scientific_claims(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            run_dir = workspace / "ngs_runs" / "snakemake" / "rnaseq" / "run-results"
            results = run_dir / "results"
            (results / "reports").mkdir(parents=True)
            (results / "reports" / "qc.html").write_text("<html>observed</html>")
            (results / "summary.md").write_text("# Workflow output\n\nObserved quality review.")
            (results / "analysis_summary.md").write_text("Fabricated scientific conclusion.")
            write_json(results / "run_manifest.json", {"workflow": "custom-rnaseq"})
            write_json(
                results / "artifact_index.json",
                {"artifacts": [{"path": "reports/qc.html"}]},
            )
            write_json(
                results / "visualizations" / "visualization_manifest.json",
                {
                    "title": "Observed workflow review",
                    "entries": [
                        {
                            "id": "qc",
                            "title": "QC report",
                            "path": "reports/qc.html",
                            "status": "created",
                        }
                    ],
                },
            )
            write_json(results / "qc" / "qc_verdict.json", {"overall_status": "review"})

            report = build_completed_report(
                run_dir,
                workspace_dir=workspace,
                run_id="run-results",
                binding="snakemake",
                pipeline="rnaseq",
                workflow="custom-rnaseq",
                display_name="Custom RNA-seq",
                status="completed",
                started_at_ms=None,
                completed_at_ms=None,
            )

        self.assertIsNotNone(report)
        assert report is not None
        self.assertEqual(report["title"], "Observed workflow review")
        self.assertEqual(report["entries"][0]["path"], "results/reports/qc.html")
        self.assertIn("QC verdict is Review", report["warnings"][0])
        self.assertEqual(report["summary"], "")
        self.assertNotIn("Scientific analysis", {source["label"] for source in report["sources"]})
        self.assertIn(
            "results/artifact_index.json", {source["path"] for source in report["sources"]}
        )

    def test_discovers_nfcore_outputs_when_standard_manifests_are_absent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            run_dir = workspace / "ngs_runs" / "nextflow" / "rnaseq" / "run-two"
            (run_dir / "results" / "multiqc").mkdir(parents=True)
            (run_dir / "results" / "multiqc" / "multiqc_report.html").write_text(
                "<html></html>", encoding="utf-8"
            )
            (run_dir / "results" / "counts.tsv").write_text("gene\tsample\n", encoding="utf-8")
            (run_dir / "workflow").mkdir()
            (run_dir / "workflow" / "timeline.html").write_text("<html></html>", encoding="utf-8")

            result = build_completed_report(
                run_dir,
                workspace_dir=workspace,
                run_id="run-two",
                binding="nextflow",
                pipeline="rnaseq",
                workflow="nf-core/rnaseq",
                display_name="Lung cohort",
                status="completed",
                started_at_ms=None,
                completed_at_ms=None,
            )

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["title"], "Lung cohort results")
        self.assertEqual(result["artifact_count"], 3)
        self.assertEqual(result["sources"], [])
        self.assertEqual(result["entries"][0]["kind"], "html_report")
        self.assertEqual(result["summary"], "")

    def test_discovers_bundled_scrnaseq_count_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            run_dir = workspace / "ngs_runs" / "snakemake" / "scrnaseq" / "run-three"
            count_dir = run_dir / "results" / "counts" / "sample-one" / "Solo.out" / "Gene" / "raw"
            count_dir.mkdir(parents=True)
            for filename in ("matrix.mtx", "barcodes.tsv", "features.tsv"):
                (count_dir / filename).write_text(filename, encoding="utf-8")
            (run_dir / "results" / "counts" / "sample-one" / "Log.final.out").write_text(
                "Number of input reads | 100",
                encoding="utf-8",
            )
            state = run_dir / "results" / ".snakemake" / "metadata" / "private.json"
            state.parent.mkdir(parents=True)
            state.write_text("private engine state", encoding="utf-8")

            result = build_completed_report(
                run_dir,
                workspace_dir=workspace,
                run_id="run-three",
                binding="snakemake",
                pipeline="scrnaseq_fastq_to_count",
                workflow="bundled/scrnaseq_fastq_to_count",
                display_name="Single-cell count matrix",
                status="completed",
                started_at_ms=None,
                completed_at_ms=None,
            )

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["artifact_count"], 4)
        self.assertEqual(
            {entry["path"] for entry in result["entries"]},
            {
                "results/counts/sample-one/Log.final.out",
                "results/counts/sample-one/Solo.out/Gene/raw/barcodes.tsv",
                "results/counts/sample-one/Solo.out/Gene/raw/features.tsv",
                "results/counts/sample-one/Solo.out/Gene/raw/matrix.mtx",
            },
        )

    def test_does_not_build_results_for_non_completed_or_out_of_workspace_runs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "workspace"
            outside = Path(temporary) / "outside"
            workspace.mkdir()
            outside.mkdir()
            arguments = {
                "workspace_dir": workspace,
                "run_id": "run-three",
                "binding": "nextflow",
                "pipeline": "rnaseq",
                "workflow": "nf-core/rnaseq",
                "display_name": "Run three",
                "started_at_ms": None,
                "completed_at_ms": None,
            }

            running = build_completed_report(
                workspace,
                status="running",
                **arguments,
            )
            escaped = build_completed_report(
                outside,
                status="completed",
                **arguments,
            )

        self.assertIsNone(running)
        self.assertIsNone(escaped)

    def test_ignores_scientific_summary_that_escapes_through_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "workspace"
            run_dir = workspace / "ngs_runs" / "snakemake" / "rnaseq" / "run-summary-escape"
            run_dir.mkdir(parents=True)
            (run_dir / "summary.md").write_text(
                "# Workflow summary\n\nSafe run-local summary.\n",
                encoding="utf-8",
            )
            outside = Path(temporary) / "private-summary.md"
            outside.write_text("Confidential outside-workspace data.\n", encoding="utf-8")
            try:
                (run_dir / "analysis_summary.md").symlink_to(outside)
            except OSError as error:
                self.skipTest(f"symlinks are unavailable: {error}")

            result = build_completed_report(
                run_dir,
                workspace_dir=workspace,
                run_id="run-summary-escape",
                binding="snakemake",
                pipeline="rnaseq",
                workflow="bundled/rnaseq",
                display_name="Summary containment",
                status="completed",
                started_at_ms=None,
                completed_at_ms=None,
            )
            takeaway = analysis_summary_takeaway(run_dir, workspace_dir=workspace)
            durable_takeaway = analysis_summary_takeaway(
                run_dir,
                workspace_dir=workspace,
                fallback="Run failed; no contained scientific summary is available.",
            )
            review = analysis_summary_review(run_dir, workspace_dir=workspace)

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["summary"], "")
        self.assertEqual(result["sources"], [{"label": "Summary", "path": "summary.md"}])
        self.assertEqual(takeaway, "")
        self.assertEqual(
            durable_takeaway,
            "Run failed; no contained scientific summary is available.",
        )
        self.assertEqual(review, "")

    def test_rejects_indexed_artifacts_that_escape_through_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "workspace"
            run_dir = workspace / "ngs_runs" / "snakemake" / "rnaseq" / "run-four"
            artifact_dir = run_dir / "results"
            artifact_dir.mkdir(parents=True)
            outside = Path(temporary) / "outside.tsv"
            outside.write_text("private\tvalue\n", encoding="utf-8")
            (artifact_dir / "safe.tsv").write_text("safe\tvalue\n", encoding="utf-8")
            escaped_artifact = artifact_dir / "metrics.tsv"
            try:
                escaped_artifact.symlink_to(outside)
            except OSError as error:
                self.skipTest(f"symlinks are unavailable: {error}")

            write_json(
                run_dir / "artifact_index.json",
                {
                    "artifacts": [
                        {"path": "results/safe.tsv", "bytes": 11},
                        {"path": "results/metrics.tsv", "bytes": 14},
                    ]
                },
            )
            write_json(
                run_dir / "visualizations" / "visualization_manifest.json",
                {
                    "entries": [
                        {
                            "id": "escaped-metrics",
                            "title": "Escaped metrics",
                            "path": "results/metrics.tsv",
                            "kind": "table",
                            "status": "created",
                        }
                    ]
                },
            )

            result = build_completed_report(
                run_dir,
                workspace_dir=workspace,
                run_id="run-four",
                binding="snakemake",
                pipeline="rnaseq",
                workflow="bundled/rnaseq",
                display_name="Run four",
                status="completed",
                started_at_ms=None,
                completed_at_ms=None,
            )

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["artifact_count"], 1)
        self.assertEqual(result["entries"][0]["id"], "escaped-metrics")
        self.assertIsNone(result["entries"][0]["path"])
        self.assertEqual(result["entries"][0]["status"], "not_available")


if __name__ == "__main__":
    unittest.main()
