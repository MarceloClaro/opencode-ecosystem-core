"""R1054 — submissão automática fail-closed, com backend explícito.

O módulo não tem backend de rede embutido e não submete nada por conta própria.
Ele faz preflight, exige confirmação humana, autorização vinculada ao hash do
manuscrito e um backend injetado. Sem esses elementos, retorna blocked.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from scientific_lab.native.common import dump, load, now, sha256_file

SCHEMA_VERSION = "1.0"
SubmissionBackend = Callable[[Path, dict], dict]


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def preflight(out: str | Path, *, profile_id: str | None = None) -> dict:
    out = Path(out).resolve()
    sub = out / "10_submission"
    reasons = []
    required = {
        "manuscript": sub / "manuscript.md",
        "manifest": sub / "submission-manifest.json",
        "checklist": sub / "journal-checklist.json",
        "declarations": sub / "declarations.json",
        "cover_letter": sub / "cover-letter.md",
    }
    for name, path in required.items():
        if not path.exists():
            reasons.append(f"missing_{name}")
    if not any((sub / name).exists() for name in ("manuscript.pdf", "manuscript.docx", "manuscript.tex")):
        reasons.append("missing_render")
    declarations = _load(sub / "declarations.json")
    if declarations:
        pending = [
            key for key, value in (declarations.get("fields") or {}).items()
            if value.get("status") == "pending_human"
        ]
        if pending:
            reasons.append("declarations_pending")
    else:
        reasons.append("declarations_missing")
    checklist = _load(sub / "journal-checklist.json")
    if checklist:
        pending_items = [
            item.get("id") for item in checklist.get("items", [])
            if item.get("status") == "pending_human"
        ]
        if pending_items:
            reasons.append("checklist_pending")
    else:
        reasons.append("checklist_missing")
    if profile_id:
        compliance = _load(sub / "journal-compliance.json")
        if not compliance:
            reasons.append("journal_compliance_missing")
        elif compliance.get("status") == "blocked":
            reasons.append("journal_compliance_blocked")
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "status": "ready" if not reasons else "blocked",
        "reasons": reasons,
        "package": str(sub),
        "profile_id": profile_id,
        "truth_claim": False,
        "external_validation": False,
        "human_review_required": True,
        "limitations": [
            "Preflight não substitui a revisão do sistema de submissão do periódico.",
            "Checklist e declarações precisam estar preenchidos por humano.",
        ],
    }


def submit(
    out: str | Path,
    *,
    profile_id: str | None = None,
    confirm: bool = False,
    backend: SubmissionBackend | None = None,
    authorization: dict | None = None,
) -> dict:
    out = Path(out).resolve()
    pre = preflight(out, profile_id=profile_id)
    attempts_path = out / "10_submission/submission-attempt.json"
    if pre["status"] != "ready":
        result = {
            **pre,
            "attempt_status": "blocked",
            "reason": "preflight_blocked",
            "submission_performed": False,
        }
        dump(attempts_path, result)
        return result
    if confirm is not True:
        result = {
            "schema_version": SCHEMA_VERSION,
            "generated_at": now(),
            "status": "blocked",
            "attempt_status": "blocked",
            "reason": "explicit_confirmation_required",
            "submission_performed": False,
            "truth_claim": False,
            "external_validation": False,
            "human_review_required": True,
        }
        dump(attempts_path, result)
        return result
    if not isinstance(authorization, dict) or authorization.get("human_confirmation") is not True:
        result = {
            "schema_version": SCHEMA_VERSION,
            "generated_at": now(),
            "status": "blocked",
            "attempt_status": "blocked",
            "reason": "authorization_required",
            "submission_performed": False,
            "truth_claim": False,
            "external_validation": False,
            "human_review_required": True,
        }
        dump(attempts_path, result)
        return result
    manuscript = out / "06_manuscript/manuscript.md"
    current_hash = sha256_file(manuscript)
    if authorization.get("manuscript_sha256") != current_hash:
        result = {
            "schema_version": SCHEMA_VERSION,
            "generated_at": now(),
            "status": "blocked",
            "attempt_status": "blocked",
            "reason": "authorization_hash_mismatch",
            "submission_performed": False,
            "truth_claim": False,
            "external_validation": False,
            "human_review_required": True,
        }
        dump(attempts_path, result)
        return result
    if backend is None:
        result = {
            "schema_version": SCHEMA_VERSION,
            "generated_at": now(),
            "status": "blocked",
            "attempt_status": "blocked",
            "reason": "no_submission_backend_configured",
            "submission_performed": False,
            "truth_claim": False,
            "external_validation": False,
            "human_review_required": True,
            "limitations": [
                "Nenhum backend de submissão foi injetado; o Core não usa portal ou credencial embutidos.",
            ],
        }
        dump(attempts_path, result)
        return result
    metadata = {
        "profile_id": profile_id,
        "manuscript_sha256": current_hash,
        "authorization": authorization,
        "package": str(out / "10_submission"),
    }
    try:
        backend_result = backend(out / "10_submission", metadata)
    except Exception as exc:
        result = {
            "schema_version": SCHEMA_VERSION,
            "generated_at": now(),
            "status": "blocked",
            "attempt_status": "failed",
            "reason": "backend_error",
            "error_type": type(exc).__name__,
            "error": str(exc)[:500],
            "submission_performed": False,
            "truth_claim": False,
            "external_validation": False,
            "human_review_required": True,
        }
        dump(attempts_path, result)
        return result
    result = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "status": "submitted" if backend_result.get("status") == "submitted" else "blocked",
        "attempt_status": backend_result.get("status"),
        "backend": backend_result,
        "submission_performed": backend_result.get("status") == "submitted",
        "manuscript_sha256": current_hash,
        "truth_claim": False,
        "external_validation": False,
        "human_review_required": True,
        "limitations": [
            "O resultado depende do backend injetado; o Core não controla o portal do periódico.",
            "Submissão não é aceite editorial nem publicação.",
        ],
    }
    dump(attempts_path, result)
    return result
