"""R1052 — leitura das decisões humanas de triagem e PRISMA com pendências.

O módulo não toma decisões. Ele lê os arquivos gravados por
``review.screen`` (que exige ``human=True``), detecta divergências entre
revisores e separa o que foi decidido do que continua pendente.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from scientific_lab.native.common import dump, load, now

SCHEMA_VERSION = "1.0"


def load_decisions(out: str | Path) -> list[dict]:
    root = Path(out) / "09_provenance/systematic_review/screening"
    decisions = []
    for path in sorted(root.glob("*.json")) if root.exists() else []:
        try:
            decision = load(path)
        except (OSError, ValueError):
            continue
        if isinstance(decision, dict):
            decisions.append(decision)
    return decisions


def _by_study(decisions: list[dict]) -> dict[str, dict[str, list[dict]]]:
    grouped: dict[str, dict[str, list[dict]]] = {}
    for decision in decisions:
        study_id = decision.get("study_id")
        stage = decision.get("stage")
        if not study_id or stage not in {"title_abstract", "full_text"}:
            continue
        grouped.setdefault(study_id, {"title_abstract": [], "full_text": []})
        grouped[study_id][stage].append(decision)
    return grouped


def summarize(studies: list[dict], decisions: list[dict]) -> dict:
    grouped = _by_study(decisions)
    rows = []
    conflict_count = 0
    single_reviewer_count = 0
    for study in studies:
        study_id = study.get("study_id")
        stages = grouped.get(study_id, {"title_abstract": [], "full_text": []})
        ta = stages["title_abstract"]
        ft = stages["full_text"]
        ta_decisions = {item.get("decision") for item in ta}
        ft_decisions = {item.get("decision") for item in ft}
        conflict = len(ta_decisions) > 1 or len(ft_decisions) > 1
        if conflict:
            conflict_count += 1
        reviewers = sorted({
            item.get("reviewer") for item in ta + ft if item.get("reviewer")
        })
        if len(reviewers) < 2 and (ta or ft):
            single_reviewer_count += 1
        if conflict:
            status = "conflict"
        elif "exclude" in ft_decisions:
            status = "excluded_full_text"
        elif "include" in ft_decisions:
            status = "included_full_text"
        elif "exclude" in ta_decisions:
            status = "excluded_title_abstract"
        elif ta_decisions == {"include"} and not ft:
            status = "awaiting_full_text"
        elif "uncertain" in ta_decisions or "uncertain" in ft_decisions:
            status = "uncertain"
        elif ta or ft:
            status = "decided_without_final_status"
        else:
            status = "pending"
        rows.append({
            "study_id": study_id,
            "title": study.get("canonical_title"),
            "status": status,
            "title_abstract_decisions": [
                {
                    "reviewer": item.get("reviewer"),
                    "decision": item.get("decision"),
                    "reason": item.get("reason"),
                    "human_decision": item.get("human_decision"),
                }
                for item in ta
            ],
            "full_text_decisions": [
                {
                    "reviewer": item.get("reviewer"),
                    "decision": item.get("decision"),
                    "reason": item.get("reason"),
                    "human_decision": item.get("human_decision"),
                }
                for item in ft
            ],
            "reviewers": reviewers,
            "conflict": conflict,
            "human_decision_count": sum(
                bool(item.get("human_decision")) for item in ta + ft
            ),
        })
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    total = len(rows)
    screened = sum(bool(row["title_abstract_decisions"]) for row in rows)
    full_text_decided = sum(bool(row["full_text_decisions"]) for row in rows)
    included = sum(row["status"] == "included_full_text" for row in rows)
    excluded = sum(
        row["status"].startswith("excluded") for row in rows
    )
    pending = sum(
        row["status"] in {"pending", "awaiting_full_text", "conflict"}
        for row in rows
    )
    all_human = all(
        decision.get("human_decision") is True
        for decision in decisions
        if decision.get("stage") == "full_text"
    ) if decisions else False
    two_reviewers = single_reviewer_count == 0 and bool(decisions)
    human_verified = (
        bool(decisions)
        and all_human
        and conflict_count == 0
        and two_reviewers
        and full_text_decided == total
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "studies": rows,
        "summary": {
            "total": total,
            "screened_title_abstract": screened,
            "full_text_decided": full_text_decided,
            "included": included,
            "excluded": excluded,
            "pending": pending,
            "conflicts": conflict_count,
            "single_reviewer_studies": single_reviewer_count,
        },
        "reviewers": sorted({
            reviewer
            for row in rows for reviewer in row["reviewers"]
        }),
        "human_verified": human_verified,
        "status": (
            "human_verified" if human_verified
            else "human_partial" if decisions
            else "pending_human"
        ),
        "policy": "decision_is_human_only",
        "truth_claim": False,
        "external_validation": False,
        "human_review_required": True,
        "limitations": [
            "A leitura depende dos arquivos de decisão gerados por review.screen.",
            "Dois revisores e ausência de conflito são requisitos de rastreabilidade, não prova de qualidade.",
            "Estudos pendentes não podem ser tratados como incluídos.",
        ],
    }


def write_summary(out: str | Path, summary: dict) -> Path:
    path = Path(out) / "02_screening/screening-summary.json"
    dump(path, summary)
    return path


def merge_into_triage(triage: dict, summary: dict) -> dict:
    by_study = {
        row["study_id"]: row for row in summary.get("studies", [])
    }
    merged = dict(triage)
    studies = []
    for item in triage.get("studies", []):
        row = by_study.get(item.get("study_id"), {})
        candidate = dict(item)
        candidate["human_screening_status"] = row.get("status", "pending")
        candidate["human_reviewers"] = row.get("reviewers", [])
        candidate["human_conflict"] = row.get("conflict", False)
        candidate["human_decision_count"] = row.get("human_decision_count", 0)
        if row.get("full_text_decisions"):
            candidate["screening_status"] = (
                "included" if row["status"] == "included_full_text"
                else "excluded" if row["status"].startswith("excluded")
                else "uncertain"
            )
        studies.append(candidate)
    merged["studies"] = studies
    merged["human_summary"] = summary.get("summary")
    merged["human_verified"] = summary.get("human_verified", False)
    merged["human_review_required"] = True
    return merged
