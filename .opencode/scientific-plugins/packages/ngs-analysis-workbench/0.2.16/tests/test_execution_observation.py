from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
MCP_ROOT = PLUGIN_ROOT / "mcp"
if str(MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(MCP_ROOT))

from ngs_workbench_execution_monitoring import (  # noqa: E402
    DEFAULT_OBSERVER_REGISTRY,
    ObserverRegistry,
)
from ngs_workbench_execution_monitoring.models import (  # noqa: E402
    MAX_RETURNED_ATTEMPTS,
    empty_observation,
)
from ngs_workbench_execution_monitoring.nextflow_trace import NextflowTraceObserver  # noqa: E402


class ExecutionObservationTests(unittest.TestCase):
    def test_nextflow_trace_discovers_processes_without_semantic_stages(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = Path(temporary)
            trace = run_dir / "workflow" / "trace.txt"
            trace.parent.mkdir()
            trace.write_text(
                "task_id\thash\tname\tstatus\texit\tsubmit\tduration\trealtime\t%cpu\tpeak_rss\tpeak_vmem\n"
                "1\taa\tNFCORE_DEMO:FASTQC (sample_1)\tCOMPLETED\t0\t2026-08-06 01:00:00\t1m\t50s\t100%\t1 GB\t2 GB\n"
                "2\tbb\tNFCORE_DEMO:MULTIQC\tFAILED\t1\t2026-08-06 01:01:00\t30s\t20s\t80%\t2 GB\t3 GB\n",
                encoding="utf-8",
            )

            observed = DEFAULT_OBSERVER_REGISTRY.observe(run_dir, "nextflow", "failed").model_dump(
                mode="json"
            )

            self.assertTrue(observed["evidence"]["available"])
            self.assertEqual(observed["counts"]["completed"], 1)
            self.assertEqual(observed["counts"]["failed"], 1)
            self.assertFalse(observed["progress"]["determinate"])
            self.assertEqual(observed["progress"]["finished_attempts"], 2)
            self.assertFalse(observed["structure"]["semantic_stages"])
            self.assertEqual(
                [process["label"] for process in observed["structure"]["processes"]],
                ["FASTQC", "MULTIQC"],
            )
            self.assertEqual(observed["attempts"][0]["sample_or_shard"], "sample_1")

    def test_nextflow_trace_ignores_partial_record_and_preserves_retries(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = Path(temporary)
            trace = run_dir / "workflow" / "trace.txt"
            trace.parent.mkdir()
            trace.write_text(
                "task_id\thash\tname\tstatus\tattempt\texit\tstart\tcomplete\tworkdir\tcontainer\n"
                "7\taa\tNFCORE:ALIGN (S1 (replicate 1))\tFAILED\t1\t1\tstart-1\tend-1\t/work/aa\taligner:1\n"
                "7\tbb\tNFCORE:ALIGN (S1 (replicate 1))\tCOMPLETED\t2\t0\tstart-2\tend-2\t/work/bb\taligner:1\n"
                "8\tcc\tNFCORE:QUANT (S1)\t",
                encoding="utf-8",
            )

            observed = DEFAULT_OBSERVER_REGISTRY.observe(run_dir, "nextflow", "running").model_dump(
                mode="json"
            )

            self.assertEqual(observed["counts"]["total"], 2)
            self.assertEqual(observed["counts"]["failed"], 1)
            self.assertEqual(observed["counts"]["completed"], 1)
            self.assertEqual(observed["evidence"]["ignored_record_count"], 1)
            self.assertEqual(
                [attempt["attempt_id"] for attempt in observed["attempts"]],
                ["7", "7:2"],
            )
            self.assertEqual(
                observed["attempts"][0]["sample_or_shard"],
                "S1 (replicate 1)",
            )
            self.assertEqual(observed["attempts"][1]["workdir"], "/work/bb")
            self.assertEqual(observed["attempts"][1]["container"], "aligner:1")

    def test_nextflow_trace_waits_for_a_complete_header(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = Path(temporary)
            trace = run_dir / "workflow" / "trace.txt"
            trace.parent.mkdir()
            trace.write_text("task_id\thash\tna", encoding="utf-8")

            observed = DEFAULT_OBSERVER_REGISTRY.observe(run_dir, "nextflow", "running").model_dump(
                mode="json"
            )

            self.assertTrue(observed["evidence"]["available"])
            self.assertEqual(observed["evidence"]["ignored_record_count"], 1)
            self.assertEqual(observed["attempts"], [])
            self.assertFalse(observed["progress"]["determinate"])

    def test_nextflow_line_parser_reports_malformed_oversized_record(self) -> None:
        observed = NextflowTraceObserver().observe_lines(
            [
                "task_id\tname\tstatus\n",
                f"1\t{'x' * 200_000}\tCOMPLETED\n",
            ],
            evidence_path="/approved/trace.txt",
            workflow_status="running",
        )

        self.assertFalse(observed.evidence.available)
        self.assertEqual(observed.evidence.path, "/approved/trace.txt")

    def test_nextflow_trace_bounds_attempt_payload_without_losing_aggregates(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = Path(temporary)
            trace = run_dir / "workflow" / "trace.txt"
            trace.parent.mkdir()
            task_count = MAX_RETURNED_ATTEMPTS + 5
            rows = "".join(
                f"{task_id}\tNFCORE:PROCESS_{task_id % 3}\tCOMPLETED\t0\n"
                for task_id in range(1, task_count + 1)
            )
            trace.write_text(
                "task_id\tname\tstatus\texit\n" + rows,
                encoding="utf-8",
            )

            observed = DEFAULT_OBSERVER_REGISTRY.observe(run_dir, "nextflow", "running").model_dump(
                mode="json"
            )

            self.assertEqual(observed["counts"]["total"], task_count)
            self.assertEqual(
                sum(process["counts"]["total"] for process in observed["structure"]["processes"]),
                task_count,
            )
            self.assertTrue(observed["attempts_truncated"])
            self.assertEqual(len(observed["attempts"]), MAX_RETURNED_ATTEMPTS)
            self.assertEqual(observed["attempts"][0]["task_id"], "6")

    def test_snakemake_native_log_normalizes_jobs_and_progress(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = Path(temporary)
            log = run_dir / "results" / ".snakemake" / "log" / "2026.snakemake.log"
            log.parent.mkdir(parents=True)
            log.write_text(
                "Job stats:\n"
                "job      count\n"
                "-------  -----\n"
                "align        1\n"
                "report       1\n"
                "all          1\n"
                "total        3\n"
                "[Thu Aug  6 01:00:00 2026]\n"
                "localrule align:\n"
                "    jobid: 4\n"
                "    wildcards: sample=S1\n"
                "[Thu Aug  6 01:00:02 2026]\n"
                "Finished jobid: 4 (Rule: align)\n"
                "1 of 3 steps (33%) done\n"
                "[Thu Aug  6 01:00:03 2026]\n"
                "localrule report:\n"
                "    jobid: 2\n",
                encoding="utf-8",
            )

            observed = DEFAULT_OBSERVER_REGISTRY.observe(
                run_dir, "snakemake", "running"
            ).model_dump(mode="json")

            self.assertEqual(observed["counts"]["completed"], 1)
            self.assertEqual(observed["progress"]["completed"], 1)
            self.assertEqual(observed["progress"]["total"], 3)
            self.assertTrue(observed["progress"]["determinate"])
            self.assertEqual(observed["counts"]["running"], 1)
            self.assertEqual(observed["attempts"][0]["process"], "align")
            self.assertEqual(observed["attempts"][0]["sample_or_shard"], "sample=S1")
            self.assertEqual(observed["evidence"]["kind"], "snakemake_native_log")
            self.assertFalse(observed["structure"]["semantic_stages"])

    def test_snakemake_native_log_preserves_retried_attempts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = Path(temporary)
            log = run_dir / "results" / ".snakemake" / "log" / "retry.snakemake.log"
            log.parent.mkdir(parents=True)
            log.write_text(
                "[Thu Aug  6 01:00:00 2026]\n"
                "localrule align:\n"
                "    jobid: 4\n"
                "    wildcards: sample=S1\n"
                "[Thu Aug  6 01:00:01 2026]\n"
                "Error in rule align:\n"
                "    jobid: 4\n"
                "[Thu Aug  6 01:00:02 2026]\n"
                "localrule align:\n"
                "    jobid: 4\n"
                "    wildcards: sample=S1\n"
                "[Thu Aug  6 01:00:03 2026]\n"
                "Finished jobid: 4 (Rule: align)\n",
                encoding="utf-8",
            )

            observed = DEFAULT_OBSERVER_REGISTRY.observe(
                run_dir, "snakemake", "completed"
            ).model_dump(mode="json")

            self.assertEqual(
                [attempt["attempt_id"] for attempt in observed["attempts"]],
                ["4:1", "4:2"],
            )
            self.assertEqual(observed["counts"]["failed"], 1)
            self.assertEqual(observed["counts"]["completed"], 1)

    def test_snakemake_terminal_status_aborts_unfinished_attempts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = Path(temporary)
            log = run_dir / "results" / ".snakemake" / "log" / "canceled.snakemake.log"
            log.parent.mkdir(parents=True)
            log.write_text(
                "[Thu Aug  6 01:00:00 2026]\n"
                "localrule align:\n"
                "    jobid: 4\n"
                "[Thu Aug  6 01:00:02 2026]\n"
                "Workflow canceled.\n",
                encoding="utf-8",
            )

            observed = DEFAULT_OBSERVER_REGISTRY.observe(
                run_dir, "snakemake", "canceled"
            ).model_dump(mode="json")

            self.assertEqual(observed["counts"]["running"], 0)
            self.assertEqual(observed["counts"]["aborted"], 1)
            self.assertEqual(observed["attempts"][0]["state"], "aborted")
            self.assertEqual(
                observed["attempts"][0]["completed_at"],
                "Thu Aug  6 01:00:02 2026",
            )

    def test_observer_registry_allows_a_binding_adapter_to_be_replaced(self) -> None:
        class MetalogSpikeObserver:
            binding = "nextflow"

            def observe(self, _run_dir: Path, _workflow_status: str):
                return empty_observation(
                    engine="nextflow",
                    evidence_kind="nf_metalog_sqlite",
                    evidence_path="/tmp/metalog.db",
                    reason="compatibility spike",
                )

        registry = ObserverRegistry({"nextflow": MetalogSpikeObserver()})

        observed = registry.observe(
            Path("/unused"),
            "nextflow",
            "running",
        ).model_dump(mode="json")

        self.assertEqual(observed["evidence"]["kind"], "nf_metalog_sqlite")


if __name__ == "__main__":
    unittest.main()
