"""Minimal FASTQ input normalization for the Snakemake binding.

This module validates request shape and local file presence. FASTQ record,
compression, read-count, and mate-pair validation belong to workflow tools.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

SAMPLE_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
FASTQ_EXTENSIONS = (".fastq", ".fq", ".fastq.gz", ".fq.gz")


def _is_remote_uri(value: str) -> bool:
    return value.startswith(("http://", "https://", "s3://", "gs://"))


def _resolve_path(value: str, base: Path) -> Path:
    path = Path(value).expanduser()
    return (path if path.is_absolute() else base / path).resolve()


def _parse_samples(
    *,
    sample_sheet: str | Path | None,
    sample_name: str | None,
    r1: str | Path | None,
    r2: str | Path | None,
) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    samples: list[dict[str, Any]] = []
    if sample_sheet and r1:
        return [], ["provide either sample_sheet or r1, not both"]
    if r2 and not r1:
        return [], ["r2 requires r1"]

    if sample_sheet:
        if _is_remote_uri(str(sample_sheet)):
            return [], ["remote sample sheets are not supported by local execution"]
        sheet = Path(sample_sheet).expanduser().resolve()
        if not sheet.is_file():
            return [], [f"sample sheet does not exist or is not a file: {sheet}"]
        sample_counts: dict[str, int] = {}
        try:
            with sheet.open(newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                columns = set(reader.fieldnames or [])
                sample_col = (
                    "sample"
                    if "sample" in columns
                    else "sample_id"
                    if "sample_id" in columns
                    else None
                )
                r1_col = "fastq_1" if "fastq_1" in columns else "r1" if "r1" in columns else None
                r2_col = "fastq_2" if "fastq_2" in columns else "r2" if "r2" in columns else None
                if not sample_col or not r1_col:
                    return [], ["sample sheet must include sample/sample_id and fastq_1/r1 columns"]
                for index, row in enumerate(reader, start=2):
                    parsed_sample = (row.get(sample_col) or "").strip()
                    parsed_r1 = (row.get(r1_col) or "").strip()
                    parsed_r2 = (row.get(r2_col) or "").strip() if r2_col else ""
                    if not parsed_sample or not parsed_r1:
                        errors.append(f"row {index}: sample and fastq_1 are required")
                        continue
                    if _is_remote_uri(parsed_r1) or (parsed_r2 and _is_remote_uri(parsed_r2)):
                        errors.append(
                            f"row {index}: remote FASTQ URLs are not supported by local execution; "
                            "download or stage files first"
                        )
                        continue
                    sample_counts[parsed_sample] = sample_counts.get(parsed_sample, 0) + 1
                    unit = (
                        parsed_sample
                        if sample_counts[parsed_sample] == 1
                        else f"{parsed_sample}__row{index}"
                    )
                    samples.append(
                        {
                            "sample": unit,
                            "original_sample": parsed_sample,
                            "r1": str(_resolve_path(parsed_r1, sheet.parent)),
                            "r2": str(_resolve_path(parsed_r2, sheet.parent))
                            if parsed_r2
                            else None,
                            "layout": "paired" if parsed_r2 else "single",
                        }
                    )
        except OSError as exc:
            return [], [f"failed to read sample sheet {sheet}: {exc}"]
    elif r1:
        if _is_remote_uri(str(r1)) or (r2 and _is_remote_uri(str(r2))):
            return [], ["remote FASTQ URLs are not supported; download or stage files first"]
        resolved_sample = sample_name or Path(r1).name.split(".")[0]
        samples.append(
            {
                "sample": resolved_sample,
                "original_sample": resolved_sample,
                "r1": str(Path(r1).expanduser().resolve()),
                "r2": str(Path(r2).expanduser().resolve()) if r2 else None,
                "layout": "paired" if r2 else "single",
            }
        )
    else:
        errors.append("provide sample_sheet or r1")

    for parsed_sample in samples:
        name = parsed_sample["sample"]
        if not SAMPLE_RE.fullmatch(name):
            errors.append(f"sample name {name!r} must match {SAMPLE_RE.pattern}")
    return samples, errors


def collect_fastq_inputs(
    *,
    sample_sheet: str | Path | None,
    sample_name: str | None,
    r1: str | Path | None,
    r2: str | Path | None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Normalize FASTQ inputs and report bounded intake errors."""
    samples, errors = _parse_samples(
        sample_sheet=sample_sheet,
        sample_name=sample_name,
        r1=r1,
        r2=r2,
    )
    summaries = []
    for sample in samples:
        paths: dict[str, Any] = {}
        for label in ("r1", "r2"):
            raw_path = sample.get(label)
            if not raw_path:
                paths[label] = None
                continue
            path = Path(raw_path)
            status = {
                "path": str(path),
                "exists": path.exists(),
                "is_file": path.is_file(),
                "recognized_extension": path.name.lower().endswith(FASTQ_EXTENSIONS),
            }
            paths[label] = status
            if not status["exists"]:
                errors.append(f"{sample['sample']} {label.upper()}: file does not exist")
            elif not status["is_file"]:
                errors.append(f"{sample['sample']} {label.upper()}: path is not a file")
            if not status["recognized_extension"]:
                errors.append(
                    f"{sample['sample']} {label.upper()}: filename does not use a recognized FASTQ extension"
                )
        summaries.append({"sample": sample["sample"], "layout": sample["layout"], **paths})

    return samples, {
        "ok": not errors,
        "scope": "intake_only",
        "content_validation": "deferred_to_workflow",
        "checks_performed": [
            "sample_sheet_shape",
            "local_path_resolution",
            "file_presence",
            "filename_extension",
        ],
        "checks_not_performed": [
            "fastq_record_structure",
            "compression_integrity",
            "read_count",
            "mate_name_pairing",
        ],
        "errors": errors,
        "warnings": [],
        "samples": summaries,
    }


def validate_trim_request(
    *, trim_mode: str, adapter_r1: str | None, samples: list[dict[str, Any]]
) -> list[str]:
    """Validate only the request shape needed to select a trim template."""
    errors: list[str] = []
    if trim_mode == "cutadapt" and not adapter_r1:
        errors.append("--trim-mode cutadapt requires --adapter-r1")
    if trim_mode != "none" and not samples:
        errors.append("trimming requested but no samples were parsed")
    return errors
