from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
MCP_ROOT = PLUGIN_ROOT / "mcp"
if str(MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(MCP_ROOT))

from ngs_workbench_mcp import preparation  # noqa: E402


class PreparationTests(unittest.TestCase):
    def _request(self, payload: bytes, destination: Path) -> dict[str, Any]:
        config = (
            json.dumps(
                {"reads": str(destination / "inputs" / "reads.fastq.gz"), "threads": 1},
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
        return {
            "destination_dir": str(destination),
            "downloads": [
                {
                    "relative_path": "inputs/reads.fastq.gz",
                    "role": "test reads",
                    "url": (
                        "https://ftp.sra.ebi.ac.uk/vol1/fastq/SRR103/008/"
                        "SRR1039508/SRR1039508_1.fastq.gz"
                    ),
                    "bytes": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                }
            ],
            "generated_files": [
                {
                    "relative_path": "config.json",
                    "media_type": "application/json",
                    "content": config,
                }
            ],
        }

    def test_rejects_invalid_requests(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "workspace"
            request = self._request(b"test-fastq\n", destination)
            request["downloads"][0]["url"] = "https:///reads.fastq.gz"
            with self.assertRaisesRegex(ValueError, "HTTPS with a host"):
                preparation.normalize_preparation(request)
            with self.assertRaisesRegex(ValueError, "Extra inputs are not permitted"):
                preparation.normalize_preparation(
                    {
                        "destination_dir": str(destination),
                        "generated_files": [
                            {
                                "relative_path": "config.txt",
                                "content": "safe\n",
                                "command": "touch /tmp/not-allowed",
                            }
                        ],
                    }
                )

    def test_normalization_binds_verified_download_and_generated_file_without_writing(self) -> None:
        payload = b"test-fastq\n"
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "workspace"
            plan = preparation.normalize_preparation(self._request(payload, destination))
            assert plan is not None

            self.assertEqual(len(plan.operations), 2)
            self.assertEqual(
                plan.operations[0].sha256, "sha256:" + hashlib.sha256(payload).hexdigest()
            )
            self.assertEqual(
                plan.operations[0].url, self._request(payload, destination)["downloads"][0]["url"]
            )
            self.assertEqual(plan.operations[0].bytes, len(payload))
            self.assertIn(
                str(destination / "inputs" / "reads.fastq.gz"), plan.operations[1].content
            )
            self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
