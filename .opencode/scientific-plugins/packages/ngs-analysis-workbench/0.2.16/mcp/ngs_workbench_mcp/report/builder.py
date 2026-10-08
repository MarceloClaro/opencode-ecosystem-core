"""Build the versioned report contract returned for a completed run."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .artifacts import build_report_entries, collect_artifacts, humanize
from .files import MAX_SUMMARY_BYTES, contained_run_directory, read_json, read_text, safe_file

_SOURCE_FILES = (
    ("Scientific analysis", "analysis_summary.md"),
    ("Summary", "summary.md"),
    ("Run manifest", "run_manifest.json"),
    ("Review manifest", "visualizations/visualization_manifest.json"),
    ("Artifact index", "artifact_index.json"),
)
_REVIEW_KINDS = {"html_report", "localhost_app", "notebook"}
_HISTORY_SUMMARY_BYTES = 8 * 1024
_HISTORY_SUMMARY_CHARACTERS = 125
_HISTORY_TAKEAWAY_PREFIX = "Takeaway:"
_DETAIL_SUMMARY_CHARACTERS = 1_200
_DETAIL_SUMMARY_SENTENCES = 6
_SUMMARY_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
_HISTORY_METADATA_QUALIFIER = re.compile(
    r",?\s+(?:identified|described|documented|recorded)\s+(?:in|by)\s+"
    r"(?:(?:existing|independently|verified|available|public|study|sample|dataset)\s+){0,6}"
    r"metadata\s+as\s+",
    re.IGNORECASE,
)
_HISTORY_EXECUTION_CLAUSE = re.compile(
    r",?\s+(?:completed|underwent|received|failed|stopped|started|"
    r"(?:analysis|execution|review)\s+(?:is|was|has|failed|stopped|remains|cannot))\b.*$",
    re.IGNORECASE,
)
_HISTORY_STATUS_LABELS = {
    "blocked": "Blocked",
    "starting": "Starting",
    "running": "Running",
    "failed": "Failed",
    "cancel_requested": "Canceling",
    "canceling": "Canceling",
    "canceled": "Canceled",
    "orphaned": "Orphaned",
    "finished_unverified": "Unverified",
}
_HISTORY_STATUS_PREFIX = re.compile(
    rf"^(?:{'|'.join(re.escape(label) for label in sorted(set(_HISTORY_STATUS_LABELS.values())))})"
    r"\s*:\s*",
    re.IGNORECASE,
)


def _output_file(root: Path, relative_path: str) -> str:
    if relative_path == "analysis_summary.md":
        return relative_path
    # CLEANUP(2026-01-09): back-compatibility. Older runs wrote workflow metadata at the run root.
    if safe_file(root, relative_path) is not None:
        return relative_path
    candidate = (Path("results") / relative_path).as_posix()
    return candidate if safe_file(root, candidate) is not None else relative_path


def _output_json(root: Path, relative_path: str, *, entries: str | None = None) -> dict[str, Any]:
    selected = _output_file(root, relative_path)
    payload = read_json(root, selected)
    if entries is None or not selected.startswith("results/"):
        return payload
    values = payload.get(entries)
    if not isinstance(values, list):
        return payload
    resolved = []
    for item in values:
        if isinstance(item, dict) and isinstance(item.get("path"), str):
            candidate = (Path("results") / item["path"]).as_posix()
            if safe_file(root, candidate) is not None:
                item = {**item, "path": candidate}
        resolved.append(item)
    return {**payload, entries: resolved}


def build_completed_report(
    run_dir: Path,
    *,
    workspace_dir: Path,
    run_id: str,
    binding: str,
    pipeline: str,
    workflow: str,
    display_name: str,
    status: str,
    started_at_ms: int | None,
    completed_at_ms: int | None,
) -> dict[str, Any] | None:
    """Project standard run files into the UI report contract after completion."""
    if status != "completed":
        return None

    root = contained_run_directory(run_dir, workspace_dir)
    if root is None:
        return None

    analysis_summary_text = read_text(root, "analysis_summary.md", MAX_SUMMARY_BYTES)
    summary_text = read_text(root, _output_file(root, "summary.md"), MAX_SUMMARY_BYTES)
    run_manifest = _output_json(root, "run_manifest.json")
    visualization = _output_json(
        root, "visualizations/visualization_manifest.json", entries="entries"
    )
    artifact_index = _output_json(root, "artifact_index.json", entries="artifacts")
    qc_verdict = _output_json(root, "qc/qc_verdict.json")

    collection = collect_artifacts(root, artifact_index)
    entries = build_report_entries(root, visualization, collection.artifacts)
    title = _report_title(display_name, pipeline, summary_text, visualization)
    description = _string(visualization.get("description")) or (
        f"Completed {workflow} analysis for registered run {run_id}."
    )
    qc_status = _string(qc_verdict.get("overall_status"))
    review_count = sum(
        entry["status"] == "created" and entry["kind"] in _REVIEW_KINDS for entry in entries
    )

    metrics = [
        {"label": "Status", "value": "Completed", "tone": "success"},
        {
            "label": "Artifacts",
            "value": f"{len(collection.artifacts)}{'+' if collection.truncated else ''}",
            "detail": "Indexed output files" if collection.indexed else "Discovered output files",
        },
        {"label": "Review items", "value": str(review_count), "detail": "Reports and notebooks"},
    ]
    if qc_status:
        metrics.append(
            {
                "label": "QC verdict",
                "value": humanize(qc_status),
                "tone": _qc_tone(qc_status),
            }
        )
    else:
        metrics.append({"label": "Engine", "value": _binding_label(binding)})

    warnings: list[str] = []
    if qc_status.lower() not in {"", "pass", "passed", "ok", "success"}:
        warnings.append(
            f"QC verdict is {humanize(qc_status)}; review qc/qc_verdict.json before downstream analysis."
        )

    return {
        "schema_version": 1,
        "title": title,
        "description": description,
        "summary": _scientific_summary(analysis_summary_text),
        "completed_at_ms": completed_at_ms,
        "duration_ms": _duration_ms(started_at_ms, completed_at_ms),
        "run_directory": str(root),
        "artifact_count": len(collection.artifacts),
        "artifact_count_truncated": collection.truncated,
        "metrics": metrics,
        "warnings": warnings,
        "entries": entries,
        "notes": _string_list(visualization.get("notes"), limit=20),
        "provenance": _provenance(binding, workflow, run_manifest),
        "sources": [
            {"label": label, "path": selected}
            for label, relative_path in _SOURCE_FILES
            if safe_file(root, selected := _output_file(root, relative_path)) is not None
        ],
    }


def _report_title(
    display_name: str,
    pipeline: str,
    summary_text: str,
    visualization: dict[str, Any],
) -> str:
    title = _string(visualization.get("title"))
    if title:
        return title
    for line in summary_text.splitlines():
        if line.lstrip().startswith("#"):
            heading = line.lstrip("# ").strip()
            if heading:
                return heading
    return f"{display_name or humanize(pipeline)} results"


def analysis_summary_review(run_dir: Path, *, workspace_dir: Path) -> str:
    """Read the concise model-authored paragraph without escaping its registered run."""
    root = contained_run_directory(run_dir, workspace_dir)
    if root is None:
        return ""
    return _scientific_summary(read_text(root, "analysis_summary.md", MAX_SUMMARY_BYTES))


def analysis_summary_takeaway(
    run_dir: Path,
    *,
    workspace_dir: Path,
    fallback: str = "",
    pipeline: str = "",
    status: str = "",
) -> str:
    """Project one complete, bounded scientific-context sentence for durable history."""
    root = contained_run_directory(run_dir, workspace_dir)
    summary_text = (
        read_text(root, "analysis_summary.md", _HISTORY_SUMMARY_BYTES) if root is not None else ""
    )
    takeaway = _dedicated_history_takeaway(summary_text) or _scientific_summary(summary_text)
    if not takeaway:
        takeaway = _dedicated_history_takeaway(fallback) or _scientific_summary(fallback)
    return analysis_summary_takeaway_text(
        takeaway,
        pipeline=pipeline,
        status=status,
    )


def analysis_summary_takeaway_text(
    summary_text: str,
    *,
    pipeline: str = "",
    status: str = "",
) -> str:
    """Project one complete history sentence from already selected summary copy."""
    takeaway = " ".join(summary_text.split())
    if not takeaway:
        return ""

    sentence = _HISTORY_STATUS_PREFIX.sub(
        "", _SUMMARY_SENTENCE_BOUNDARY.split(takeaway, maxsplit=1)[0]
    ).strip()
    workflow = {
        "fastq_qc": "FastQC",
        "rnaseq": "Bulk RNA-seq",
        "scrnaseq": "Single-cell RNA-seq",
    }.get(pipeline, "")
    status_label = _HISTORY_STATUS_LABELS.get(status)
    labeled_sentence = f"{status_label}: {sentence}" if status_label and sentence else sentence
    if len(labeled_sentence) <= _HISTORY_SUMMARY_CHARACTERS:
        return _bounded_history_sentence(labeled_sentence or status_label or "")

    context = _HISTORY_METADATA_QUALIFIER.sub(" from ", sentence)
    context = _HISTORY_EXECUTION_CLAUSE.sub("", context)
    context = re.sub(
        r"\s+(?:are|is|were|was)\s+(?:suitable|appropriate|ready|adequate|sufficient)\s+for\b.*$",
        "",
        context,
        flags=re.IGNORECASE,
    )
    context = re.sub(r"\bRNA[- ]sequencing\b", "RNA-seq", context, flags=re.IGNORECASE)
    context = re.sub(r"\s+discussed\s+in\s+", " in ", context, flags=re.IGNORECASE)
    context = re.sub(r"^the\s+", "", context, flags=re.IGNORECASE).strip(" ,;:.")
    context = re.sub(
        r"^(this|these|that|those)\b",
        lambda match: match.group(1).lower(),
        context,
        flags=re.IGNORECASE,
    )
    if not workflow:
        workflow_match = re.search(r"\b(?:FastQC|STARsolo|Salmon|MultiQC)\b", sentence)
        workflow = workflow_match.group(0) if workflow_match else ""

    concise = context
    if (
        workflow
        and context
        and not context.endswith("?")
        and not context.lower().startswith(workflow.lower())
    ):
        concise = f"{workflow} on {context}"

    if status_label:
        reason_match = re.search(r"\bbecause\s+([^.!?]+)", sentence, re.IGNORECASE)
        if reason_match and concise:
            reason = reason_match.group(1).strip()
            if reason.lower() not in concise.lower():
                prefix = f"{status_label}: "
                suffix = f"; {reason}"
                context_limit = _HISTORY_SUMMARY_CHARACTERS - len(prefix) - len(suffix) - 1
                if context_limit > 0:
                    concise = f"{prefix}{_bounded_history_fragment(concise, context_limit)}{suffix}"
                else:
                    concise = f"{prefix}{reason}"
            else:
                concise = f"{status_label}: {concise}"
        else:
            concise = f"{status_label}: {concise}" if concise else status_label

    return _bounded_history_sentence(concise or sentence)


def _bounded_history_sentence(value: str) -> str:
    """Finish history copy at a word boundary without displaying an ellipsis."""
    value = re.sub(r"(?:…|\.{3})+$", "", value.strip()).rstrip(" ,;:")
    if not value:
        return ""
    if len(value) <= _HISTORY_SUMMARY_CHARACTERS and value.endswith((".", "!", "?")):
        return value

    body = value.rstrip(".!?")
    limit = _HISTORY_SUMMARY_CHARACTERS - 1
    body = _bounded_history_fragment(body, limit)
    return f"{body}." if body else ""


def _bounded_history_fragment(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    bounded = value[:limit].rstrip()
    if not value[limit].isspace():
        boundary = bounded.rfind(" ")
        if boundary > 0:
            bounded = bounded[:boundary]
    bounded = re.sub(r"\s+(?:a|an|the|of|for|on|in|from|with|and|or|to|by)$", "", bounded)
    return bounded.rstrip(" ,;:-")


def _dedicated_history_takeaway(summary_text: str) -> str:
    """Read the optional model-authored history sentence from the existing review."""
    for raw_line in summary_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(_HISTORY_TAKEAWAY_PREFIX):
            return _plain_summary_text(line.removeprefix(_HISTORY_TAKEAWAY_PREFIX).strip())
        break
    return ""


def _scientific_summary(summary_text: str) -> str:
    """Project only the opening, plain-language scientific narrative into the UI."""
    paragraph: list[str] = []
    for raw_line in summary_text.splitlines():
        line = raw_line.strip()
        if not line:
            if paragraph:
                break
            continue
        if line.startswith("#"):
            if paragraph:
                break
            continue
        if not paragraph and line.startswith(_HISTORY_TAKEAWAY_PREFIX):
            continue
        if line.startswith("|"):
            if paragraph:
                break
            continue
        plain_line = _plain_summary_text(line.removeprefix("- "))
        if plain_line:
            paragraph.append(plain_line)

    narrative = " ".join(" ".join(paragraph).split())
    if not narrative:
        return ""

    return " ".join(_SUMMARY_SENTENCE_BOUNDARY.split(narrative)[:_DETAIL_SUMMARY_SENTENCES])[
        :_DETAIL_SUMMARY_CHARACTERS
    ].rstrip()


def _plain_summary_text(value: str) -> str:
    value = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"(?<!\w)_{1,2}([^_]+)_{1,2}(?!\w)", r"\1", value)
    return value.replace("`", "").replace("*", "").replace("~~", "")


def _provenance(binding: str, workflow: str, manifest: dict[str, Any]) -> list[dict[str, str]]:
    values = [
        ("Engine", _binding_label(binding)),
        ("Workflow", _string(manifest.get("workflow")) or workflow),
        ("Manifest schema", _string(manifest.get("schema_version"))),
    ]
    audit = manifest.get("audit") if isinstance(manifest.get("audit"), dict) else {}
    parameter_hash = _string(audit.get("parameter_sha256"))
    if parameter_hash:
        values.append(("Parameter SHA256", parameter_hash))
    return [{"label": label, "value": value} for label, value in values if value]


def _duration_ms(started_at_ms: int | None, completed_at_ms: int | None) -> int | None:
    if started_at_ms is None or completed_at_ms is None or completed_at_ms < started_at_ms:
        return None
    return completed_at_ms - started_at_ms


def _qc_tone(status: str) -> str:
    normalized = status.lower()
    if normalized in {"pass", "passed", "ok", "success"}:
        return "success"
    if normalized in {"fail", "failed", "blocked", "error"}:
        return "danger"
    return "warning"


def _binding_label(binding: str) -> str:
    return humanize(binding)


def _string(value: object) -> str:
    return value.strip()[:2_000] if isinstance(value, str) else ""


def _string_list(value: object, *, limit: int) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_string(item)[:500] for item in value if _string(item)][:limit]
