from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
MCP_ROOT = PLUGIN_ROOT / "mcp"
FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "execution_observation"
if str(MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(MCP_ROOT))

from ngs_workbench_execution_monitoring import DEFAULT_OBSERVER_REGISTRY  # noqa: E402
from ngs_workbench_execution_monitoring.nextflow_trace import NextflowTraceObserver  # noqa: E402
from ngs_workbench_execution_monitoring.snakemake_log import SnakemakeLogObserver  # noqa: E402


class RecordedExecutionObservationGoldenTests(unittest.TestCase):
    maxDiff = None

    def test_recorded_nextflow_trace_matches_complete_golden(self) -> None:
        self._assert_recorded_observation_matches("nextflow")

    def test_recorded_snakemake_log_matches_complete_golden(self) -> None:
        self._assert_recorded_observation_matches("snakemake")

    def test_shared_line_api_matches_local_adapters(self) -> None:
        manifests = json.loads((FIXTURE_ROOT / "fixture_manifest.json").read_text(encoding="utf-8"))
        for fixture_name, observer in (
            ("nextflow", NextflowTraceObserver()),
            ("snakemake", SnakemakeLogObserver()),
        ):
            with self.subTest(binding=fixture_name):
                manifest = manifests[fixture_name]
                run_dir = FIXTURE_ROOT / fixture_name
                fixture_path = FIXTURE_ROOT / manifest["fixture_path"]
                local = DEFAULT_OBSERVER_REGISTRY.observe(
                    run_dir,
                    manifest["binding"],
                    manifest["workflow_status"],
                ).model_dump(mode="json")
                with fixture_path.open(encoding="utf-8-sig", newline="") as lines:
                    streamed = observer.observe_lines(
                        lines,
                        evidence_path=str(fixture_path),
                        workflow_status=manifest["workflow_status"],
                    ).model_dump(mode="json")

                self.assertEqual(streamed, local)

    def _assert_recorded_observation_matches(self, fixture_name: str) -> None:
        manifest = json.loads((FIXTURE_ROOT / "fixture_manifest.json").read_text(encoding="utf-8"))[
            fixture_name
        ]
        fixture_path = FIXTURE_ROOT / manifest["fixture_path"]
        self.assertEqual(
            hashlib.sha256(fixture_path.read_bytes()).hexdigest(),
            manifest["fixture_sha256"],
            "recorded fixture changed; update its provenance and golden intentionally",
        )

        run_dir = FIXTURE_ROOT / fixture_name
        observed = DEFAULT_OBSERVER_REGISTRY.observe(
            run_dir,
            manifest["binding"],
            manifest["workflow_status"],
        ).model_dump(mode="json")
        observed["evidence"]["path"] = (
            Path(observed["evidence"]["path"]).relative_to(run_dir).as_posix()
        )
        expected = json.loads((FIXTURE_ROOT / manifest["golden_path"]).read_text(encoding="utf-8"))

        self.assertEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
