"""R1052 — integridade de literatura: retratações, correções e atualizações.

Consulta o Crossref por DOI e registra o que encontrou. Não declara que um
artigo é válido por não ter atualização; ausência de registro não é prova de
integridade. O resultado é sempre uma observação datada e limitada.
"""
from __future__ import annotations

import hashlib
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable

from scientific_lab.native.common import dump, load, now, uid

SCHEMA_VERSION = "1.0"
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)
RETRACTION_HINTS = ("retract", "withdraw")
CORRECTION_HINTS = ("correct", "corrigendum", "erratum")
UPDATE_HINTS = ("update", "new-version", "version")


def _normalize_doi(value: object) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"^https?://(dx\.)?doi\.org/", "", text)
    text = re.sub(r"^doi:\s*", "", text)
    return text.strip().rstrip(".,;)")


def _validate_doi(doi: str) -> str:
    if not DOI_RE.match(doi):
        raise ValueError("DOI inválido")
    return doi


def _safe_error(exc: Exception) -> str:
    text = f"{type(exc).__name__}: {exc}"
    text = re.sub(
        r"(?i)(api[_-]?key|token|authorization|secret)\s*[=:]\s*\S+",
        r"\1=[redacted]",
        text,
    )
    return text[:300]


def _relation_updates(message: dict) -> list[dict]:
    updates = []
    relations = message.get("relation") or {}
    if isinstance(relations, dict):
        for relation, items in relations.items():
            if not isinstance(items, list):
                continue
            for item in items:
                if isinstance(item, dict):
                    updates.append({
                        "relation": relation,
                        "id": item.get("id"),
                        "id_type": item.get("id-type"),
                        "asserted_by": item.get("asserted-by"),
                    })
    update_to = message.get("update-to") or []
    if isinstance(update_to, list):
        for item in update_to:
            if isinstance(item, dict):
                updates.append({
                    "relation": "update-to",
                    "id": item.get("DOI") or item.get("doi"),
                    "id_type": "doi",
                    "type": item.get("type"),
                })
    return updates


def classify_updates(updates: list[dict], message: dict) -> str:
    text = " ".join(
        str(item.get("relation") or "") + " " + str(item.get("type") or "")
        for item in updates
    ).lower()
    if any(hint in text for hint in RETRACTION_HINTS):
        return "retracted"
    if message.get("type") == "retraction":
        return "retracted_notice"
    if any(hint in text for hint in CORRECTION_HINTS):
        return "correction"
    if any(hint in text for hint in UPDATE_HINTS):
        return "update"
    return "no_update_found"


def check_crossref(
    doi: str,
    *,
    timeout: int = 20,
    opener: Callable[[str, int], tuple[int, bytes]] | None = None,
) -> dict:
    """Consulta um DOI no Crossref. ``opener`` é injetável para testes."""
    doi = _validate_doi(_normalize_doi(doi))
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    if opener is None:
        def opener(target: str, seconds: int):
            request = urllib.request.Request(
                target,
                headers={
                    "User-Agent": "opencode-ecosystem-core/1.0 (research integrity)",
                    "Accept": "application/json",
                },
            )
            with urllib.request.urlopen(request, timeout=seconds) as response:
                return response.status, response.read(4_000_000)
    status, body = opener(url, timeout)
    if status != 200:
        raise RuntimeError(f"Crossref retornou HTTP {status}")
    message = json.loads(body.decode("utf-8")).get("message") or {}
    updates = _relation_updates(message)
    return {
        "schema_version": SCHEMA_VERSION,
        "doi": doi,
        "status": classify_updates(updates, message),
        "updates": updates,
        "crossref_type": message.get("type"),
        "crossref_title": (message.get("title") or [None])[0],
        "checked_at": now(),
        "response_sha256": hashlib.sha256(body).hexdigest(),
        "source": "crossref",
        "limitations": [
            "Crossref pode não registrar toda retratação, correção ou versão.",
            "Ausência de atualização não prova integridade científica.",
        ],
    }


def check_many(
    studies: list[dict],
    *,
    checker: Callable[[str], dict] | None = None,
    max_checks: int = 20,
    timeout: int = 20,
) -> dict:
    """Verifica até ``max_checks`` estudos com DOI, sem esconder falhas."""
    if isinstance(max_checks, bool) or not isinstance(max_checks, int) or max_checks < 0:
        raise ValueError("max_checks inválido")
    checks = []
    used = 0
    for study in studies:
        doi = _normalize_doi((study.get("identifiers") or {}).get("doi"))
        base = {
            "study_id": study.get("study_id"),
            "doi": doi or None,
        }
        if not doi:
            checks.append({
                **base,
                "status": "unchecked",
                "reason": "no_doi",
                "updates": [],
                "checked_at": now(),
                "limitations": ["Estudo sem DOI; integridade não verificada."],
            })
            continue
        if used >= max_checks:
            checks.append({
                **base,
                "status": "unchecked",
                "reason": "budget_exhausted",
                "updates": [],
                "checked_at": now(),
                "limitations": ["Orçamento de verificações esgotado."],
            })
            continue
        used += 1
        try:
            result = checker(doi) if checker is not None else check_crossref(
                doi, timeout=timeout,
            )
            checks.append({**base, **result})
        except Exception as exc:
            checks.append({
                **base,
                "status": "error",
                "reason": _safe_error(exc),
                "updates": [],
                "checked_at": now(),
                "limitations": ["Falha ao consultar o Crossref; não interpretar como ausência de retratação."],
            })
    statuses = {}
    for check in checks:
        statuses[check["status"]] = statuses.get(check["status"], 0) + 1
    return {
        "schema_version": SCHEMA_VERSION,
        "check_id": uid("INTEG", 12),
        "generated_at": now(),
        "checks": checks,
        "summary": statuses,
        "checked": used,
        "policy": "absence_of_update_is_not_proof_of_integrity",
        "truth_claim": False,
        "external_validation": False,
        "human_review_required": True,
        "limitations": [
            "A consulta é limitada ao Crossref e ao orçamento configurado.",
            "Retratações podem estar apenas no site do editor ou em outras bases.",
            "O status no_update_found não é atestado de integridade.",
        ],
    }


def write_checks(out: str | Path, result: dict) -> Path:
    path = Path(out) / "03_evidence/integrity-checks.json"
    dump(path, result)
    return path


def apply_to_studies(
    out: str | Path,
    result: dict,
) -> dict:
    """Atualiza ``integrity_status`` dos estudos e grava o mapa de integridade."""
    out = Path(out)
    mapping = {
        check["study_id"]: check["status"]
        for check in result.get("checks", [])
        if check.get("study_id")
    }
    studies_dir = out / "01_sources/systematic_review/studies"
    updated = []
    for path in sorted(studies_dir.glob("*.json")):
        study = load(path)
        study_id = study.get("study_id")
        if study_id in mapping:
            study["integrity_status"] = mapping[study_id]
            study["integrity_checked_at"] = now()
            dump(path, study)
            updated.append({
                "study_id": study_id,
                "integrity_status": mapping[study_id],
            })
    dump(out / "03_evidence/study-integrity.json", {
        "schema_version": SCHEMA_VERSION,
        "updated": updated,
        "count": len(updated),
        "policy": "status_is_observational_not_certification",
        "human_review_required": True,
    })
    return {"updated": updated, "count": len(updated)}
