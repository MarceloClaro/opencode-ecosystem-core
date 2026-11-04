"""R1054 — extração automática de efeitos de texto integral.

A extração é conservadora e marcada como automatizada. Ela produz candidatos
com página/parágrafo, recorte literal, medida, efeito, erro-padrão (quando
derivável) e confiança. O dataset quantitativo gerado é um rascunho
``automated_draft``; não é uma extração validada por dois revisores.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import statistics
from pathlib import Path
from typing import Any

from scientific_lab import fulltext
from scientific_lab.native.common import dump, now, uid

SCHEMA_VERSION = "1.0"
LOG_MEASURES = {"OR", "RR", "HR"}
IDENTITY_MEASURES = {"SMD", "MD", "D", "G"}
ALL_MEASURES = LOG_MEASURES | IDENTITY_MEASURES

MEASURE_PATTERN = (
    r"odds ratio|risk ratio|hazard ratio|OR|RR|HR|SMD|MD|"
    r"Hedges'? g|Cohen'?s d|\bd\b|\bg\b"
)
LINK_PATTERN = r"\s*(?:(?:was|were|is|are|of)\s*)?(?:=|:)?\s*"
CI_PATTERN = re.compile(
    rf"(?P<measure>{MEASURE_PATTERN}){LINK_PATTERN}"
    r"(?P<effect>-?\d+(?:\.\d+)?)"
    r"[^.\n]{0,80}?"
    r"(?:95\s*%\s*CI|CI)\s*(?:=|:)?\s*"
    r"(?P<low>-?\d+(?:\.\d+)?)\s*(?:to|–|—|-|,)\s*"
    r"(?P<high>-?\d+(?:\.\d+)?)",
    re.IGNORECASE,
)
SE_PATTERN = re.compile(
    rf"(?P<measure>{MEASURE_PATTERN}){LINK_PATTERN}"
    r"(?P<effect>-?\d+(?:\.\d+)?)"
    r"[^.\n]{0,80}?\bSE\s*(?:=|:)?\s*(?P<se>\d+(?:\.\d+)?)",
    re.IGNORECASE,
)
P_PATTERN = re.compile(
    rf"(?P<measure>{MEASURE_PATTERN}){LINK_PATTERN}"
    r"(?P<effect>-?\d+(?:\.\d+)?)"
    r"[^.\n]{0,80}?\bp\s*(?:=|<)\s*(?P<p>0?\.\d+|\d+\.\d+)",
    re.IGNORECASE,
)
EFFECT_PATTERN = re.compile(
    rf"(?P<measure>{MEASURE_PATTERN}){LINK_PATTERN}"
    r"(?P<effect>-?\d+(?:\.\d+)?)",
    re.IGNORECASE,
)


def _measure(value: str) -> str:
    text = value.strip().lower()
    if "odds" in text:
        return "OR"
    if "risk ratio" in text:
        return "RR"
    if "hazard" in text:
        return "HR"
    if "hedges" in text or text == "g":
        return "G"
    if "cohen" in text or text == "d":
        return "D"
    return text.upper()


def _z(level: float = 0.95) -> float:
    return statistics.NormalDist().inv_cdf(1 - (1 - level) / 2)


def _sentence(text: str, start: int, end: int) -> str:
    left = max(text.rfind(".", 0, start), text.rfind("\n", 0, start))
    right = min(
        [index for index in (text.find(".", end), text.find("\n", end)) if index >= 0]
        or [len(text)]
    )
    return " ".join(text[left + 1:right + 1].split())[:600]


def _se_from_ci(measure: str, low: float, high: float) -> tuple[float, str]:
    width = high - low
    if width <= 0:
        raise ValueError("intervalo de confiança inválido")
    if measure in LOG_MEASURES:
        return (math.log(high) - math.log(low)) / (2 * _z()), "ci_log"
    return width / (2 * _z()), "ci_identity"


def _se_from_p(measure: str, effect: float, p: float) -> tuple[float, str]:
    if not 0 < p < 1:
        raise ValueError("p-valor inválido")
    z = statistics.NormalDist().inv_cdf(1 - p / 2)
    value = math.log(effect) if measure in LOG_MEASURES else effect
    return abs(value) / z, "p_value"


def extract_from_text(text: str, *, source: str = "text") -> list[dict]:
    candidates = []
    seen = set()

    def add(match: re.Match, *, se: float | None, method: str, confidence: float):
        measure = _measure(match.group("measure"))
        effect = float(match.group("effect"))
        if measure in LOG_MEASURES and effect <= 0:
            return
        analysis_effect = math.log(effect) if measure in LOG_MEASURES else effect
        quote = _sentence(text, match.start(), match.end())
        key = (measure, round(effect, 8), round(se, 8) if se is not None else None)
        if key in seen:
            return
        seen.add(key)
        candidates.append({
            "candidate_id": uid("EFF", 10),
            "source": source,
            "measure": measure,
            "reported_effect": effect,
            "analysis_effect": analysis_effect,
            "analysis_scale": "log" if measure in LOG_MEASURES else "identity",
            "standard_error": se,
            "se_method": method,
            "confidence": confidence,
            "status": "complete" if se is not None else "incomplete",
            "quote": quote,
            "automated": True,
            "human_review_required": True,
        })

    for match in CI_PATTERN.finditer(text):
        measure = _measure(match.group("measure"))
        try:
            se, method = _se_from_ci(
                measure, float(match.group("low")), float(match.group("high")),
            )
        except ValueError:
            continue
        add(match, se=se, method=method, confidence=0.9)
    for match in SE_PATTERN.finditer(text):
        add(match, se=float(match.group("se")), method="reported_se", confidence=0.8)
    for match in P_PATTERN.finditer(text):
        measure = _measure(match.group("measure"))
        try:
            se, method = _se_from_p(
                measure, float(match.group("effect")), float(match.group("p")),
            )
        except ValueError:
            continue
        add(match, se=se, method=method, confidence=0.7)
    for match in EFFECT_PATTERN.finditer(text):
        add(match, se=None, method="not_reported", confidence=0.4)
    complete_keys = {
        (item["measure"], round(item["reported_effect"], 8))
        for item in candidates if item["status"] == "complete"
    }
    return [
        item for item in candidates
        if item["status"] == "complete"
        or (item["measure"], round(item["reported_effect"], 8)) not in complete_keys
    ]


def extract_from_index(
    index: dict,
    matches: dict,
    studies: list[dict],
    records: list[dict],
    *,
    max_candidates_per_study: int = 3,
) -> dict:
    entries = {entry["fulltext_id"]: entry for entry in index["entries"]}
    studies_by_id = {study["study_id"]: study for study in studies}
    by_article = {record["article_id"]: record for record in records}
    candidates = []
    for match in matches["matches"]:
        if match.get("duplicate_for_study"):
            continue
        entry = entries.get(match["fulltext_id"])
        study = studies_by_id.get(match["study_id"])
        if entry is None or study is None:
            continue
        article_id = (study.get("source_records") or [None])[0]
        record = by_article.get(article_id, {})
        found = []
        for page in entry["pages"]:
            for candidate in extract_from_text(
                page["text"], source=f"{entry['path']}:{page['page']}",
            ):
                candidate.update({
                    "study_id": study["study_id"],
                    "article_id": article_id,
                    "fulltext_id": entry["fulltext_id"],
                    "page": page["page"],
                    "locator": (
                        f"p.{page['page']}" if entry["format"] == "pdf"
                        else f"par.{page['page']}"
                    ),
                    "source_file": entry["path"],
                    "source_sha256": entry["sha256"],
                    "quote_sha256": hashlib.sha256(
                        candidate["quote"].encode("utf-8")
                    ).hexdigest(),
                    "title": study.get("canonical_title") or record.get("title"),
                })
                found.append(candidate)
        found.sort(key=lambda item: (-item["confidence"], item["page"]))
        candidates.extend(found[:max_candidates_per_study])
    return {
        "schema_version": SCHEMA_VERSION,
        "extraction_id": uid("EXTRACT", 12),
        "generated_at": now(),
        "status": "completed",
        "candidates": candidates,
        "count": len(candidates),
        "complete": sum(item["status"] == "complete" for item in candidates),
        "incomplete": sum(item["status"] == "incomplete" for item in candidates),
        "policy": "automated_candidate_not_verified",
        "truth_claim": False,
        "external_validation": False,
        "human_review_required": True,
        "limitations": [
            "A extração usa regex e pode confundir medidas, escalas e intervalos.",
            "Ela não lê tabelas, figuras ou texto em PDF sem camada textual.",
            "Todo candidato exige conferência humana antes de entrar na meta-análise.",
        ],
    }


def write_candidates(out: str | Path, result: dict) -> Path:
    path = Path(out) / "04_analysis/auto-effect-candidates.json"
    dump(path, result)
    return path


def draft_quantitative_dataset(
    candidates: list[dict],
    *,
    reviewer: str,
    human_confirmation: bool = False,
    model: str = "random",
    random_effects_method: str = "REML",
    max_per_study: int = 1,
) -> dict:
    if human_confirmation is not True:
        raise ValueError("rascunho automático exige human_confirmation=true")
    if not reviewer or len(reviewer.strip()) < 2:
        raise ValueError("rascunho automático exige reviewer")
    complete = [item for item in candidates if item.get("standard_error")]
    by_study: dict[str, list[dict]] = {}
    for item in complete:
        by_study.setdefault(item["study_id"], []).append(item)
    chosen = []
    rejected = []
    for study_id, items in by_study.items():
        items.sort(key=lambda item: (-item["confidence"], item["page"]))
        chosen.extend(items[:max_per_study])
        rejected.extend(items[max_per_study:])
    measures = {item["measure"] for item in chosen}
    if len(measures) != 1:
        raise ValueError(
            "medidas mistas exigem decisão humana: " + ", ".join(sorted(measures))
        )
    measure = measures.pop()
    studies = []
    for item in chosen:
        studies.append({
            "study_id": item["study_id"],
            "label": item.get("title") or item["study_id"],
            "effect_size": item["analysis_effect"],
            "standard_error": item["standard_error"],
            "design": "not_reported",
            "outcome": "not_reported",
            "risk_of_bias": {
                "overall": "not_assessed",
                "domains": {"automated_extraction": "not_assessed"},
            },
            "extraction": {
                "candidate_id": item["candidate_id"],
                "locator": item["locator"],
                "source_file": item["source_file"],
                "source_sha256": item["source_sha256"],
                "quote": item["quote"],
                "confidence": item["confidence"],
                "automated": True,
            },
        })
    if len(studies) < 2:
        raise ValueError("rascunho automático exige ao menos dois estudos completos")
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "automated_draft",
        "project_id": None,
        "protocol": {
            "reviewer": reviewer.strip(),
            "declared_at": now(),
            "effect_measure": measure,
            "analysis_scale": "log" if measure in LOG_MEASURES else "identity",
            "model": model,
            "random_effects_method": random_effects_method,
            "confidence_level": 0.95,
            "min_studies": 2,
            "max_i2_for_pooling": 75,
            "human_confirmation": True,
            "automated_extraction": True,
        },
        "studies": studies,
        "extraction_summary": {
            "candidates_total": len(candidates),
            "complete_candidates": len(complete),
            "studies_used": len(studies),
            "candidates_rejected": len(rejected),
            "measure": measure,
        },
        "truth_claim": False,
        "external_validation": False,
        "human_review_required": True,
        "limitations": [
            "Dataset gerado por regex; não foi validado por dois revisores.",
            "Medidas mistas, tabelas e figuras não são extraídas automaticamente.",
            "Risco de viés permanece not_assessed até julgamento humano.",
        ],
    }


def write_draft(out: str | Path, draft: dict) -> Path:
    path = Path(out) / "04_analysis/auto-quantitative-draft.json"
    dump(path, draft)
    return path


def run(
    out: str | Path,
    fulltext_dir: str | Path,
    studies: list[dict],
    records: list[dict],
    *,
    reviewer: str,
    human_confirmation: bool = False,
    write_draft_file: bool = True,
) -> dict:
    index = fulltext.index_fulltexts(fulltext_dir)
    matches = fulltext.match_entries(index, studies, records)
    result = extract_from_index(index, matches, studies, records)
    write_candidates(out, result)
    draft = draft_quantitative_dataset(
        result["candidates"], reviewer=reviewer,
        human_confirmation=human_confirmation,
    )
    if write_draft_file:
        write_draft(out, draft)
    return {"candidates": result, "draft": draft}
