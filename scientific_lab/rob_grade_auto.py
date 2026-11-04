"""R1054 — risco de viés e GRADE automáticos como sugestão auditável.

As regras são heurísticas explícitas. Elas não substituem julgamento humano e
nunca são marcadas como ``authoritative``. O resultado pode alimentar o módulo
quantitativo apenas com ``human_confirmation=true``.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from scientific_lab import fulltext, quantitative
from scientific_lab.native.common import dump, now, uid

SCHEMA_VERSION = "1.0"
RULE_VERSION = "R1054.1"
ROB_ORDER = {"high": 3, "some_concerns": 2, "low": 1, "not_assessed": 0}
GRADE_ORDER = {"high": 4, "moderate": 3, "low": 2, "very_low": 1}
GRADE_NAMES = {value: key for key, value in GRADE_ORDER.items()}


def _text_value(text: str) -> str:
    return " ".join((text or "").lower().split())


def _missing_percent(text: str) -> float | None:
    match = re.search(
        r"(?:missing|loss to follow-up|attrition|perdidos?)[^.%]{0,80}?"
        r"(\d+(?:\.\d+)?)\s*%",
        text,
        re.IGNORECASE,
    )
    if match:
        return float(match.group(1))
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*%[^.]{0,80}?"
        r"(?:missing|loss to follow-up|attrition|perdidos?)",
        text,
        re.IGNORECASE,
    )
    return float(match.group(1)) if match else None


def assess_risk_of_bias(text: str, design: str | None = None) -> dict:
    body = _text_value(text)
    domains = {}
    reasons = {}
    if "randomly assigned" in body or "randomized" in body or "randomised" in body:
        domains["randomization"] = "low"
        reasons["randomization"] = "texto declara alocação aleatória"
    elif any(token in body for token in ("quasi-experimental", "alternate", "non-random")):
        domains["randomization"] = "high"
        reasons["randomization"] = "texto indica alocação não aleatória"
    elif any(token in body for token in ("observational", "cohort", "case-control")):
        domains["randomization"] = "high"
        reasons["randomization"] = "desenho observacional"
    else:
        domains["randomization"] = "not_assessed"
        reasons["randomization"] = "alocação não identificada"

    if "intention-to-treat" in body or re.search(r"\bitt\b", body):
        domains["deviations"] = "low"
        reasons["deviations"] = "texto declara intenção de tratar"
    elif "per-protocol" in body:
        domains["deviations"] = "some_concerns"
        reasons["deviations"] = "texto menciona análise por protocolo"
    else:
        domains["deviations"] = "not_assessed"
        reasons["deviations"] = "desvios não identificados"

    missing = _missing_percent(body)
    if missing is None:
        domains["missing"] = "not_assessed"
        reasons["missing"] = "percentual de dados faltantes não identificado"
    elif missing > 20:
        domains["missing"] = "high"
        reasons["missing"] = f"{missing:.1f}% de dados faltantes"
    elif missing > 10:
        domains["missing"] = "some_concerns"
        reasons["missing"] = f"{missing:.1f}% de dados faltantes"
    else:
        domains["missing"] = "low"
        reasons["missing"] = f"{missing:.1f}% de dados faltantes"

    if "double-blind" in body or "blinded" in body or "masked" in body:
        domains["measurement"] = "low"
        reasons["measurement"] = "texto declara cegamento"
    elif "self-reported" in body or "self reported" in body:
        domains["measurement"] = "some_concerns"
        reasons["measurement"] = "desfecho auto-relatado"
    else:
        domains["measurement"] = "not_assessed"
        reasons["measurement"] = "cegamento não identificado"

    if "registered" in body or "pre-registered" in body or "protocol" in body:
        domains["selection"] = "low"
        reasons["selection"] = "texto menciona registro/protocolo"
    else:
        domains["selection"] = "not_assessed"
        reasons["selection"] = "registro seletivo não identificado"

    overall = max(domains.values(), key=lambda value: ROB_ORDER[value])
    return {
        "schema_version": SCHEMA_VERSION,
        "overall": overall,
        "domains": domains,
        "reasons": reasons,
        "design": design,
        "automated": True,
        "authoritative": False,
        "rule_version": RULE_VERSION,
        "human_review_required": True,
        "limitations": [
            "Regras heurísticas sobre texto; não substituem RoB 2/ROBINS-I.",
            "Ausência de menção não é ausência de risco.",
        ],
    }


def assess_grade(
    meta_result: dict,
    texts: list[str],
    *,
    reviewer: str,
    human_confirmation: bool = False,
) -> dict:
    if human_confirmation is not True:
        raise ValueError("GRADE automático exige human_confirmation=true")
    if not reviewer or len(reviewer.strip()) < 2:
        raise ValueError("GRADE automático exige reviewer")
    body = _text_value(" ".join(texts))
    rct = "randomized" in body or "randomised" in body or "randomly assigned" in body
    starting = "high" if rct else "low"
    domains = {}

    high_risk = (meta_result.get("risk_of_bias") or {}).get("studies_with_high_risk", 0)
    domains["risk_of_bias"] = {
        "judgment": "serious" if high_risk else "not_serious",
        "reason": (
            f"{high_risk} estudo(s) com risco de viés alto"
            if high_risk else "nenhum estudo marcado como alto risco"
        ),
    }

    i2 = float((meta_result.get("heterogeneity") or {}).get("i2_percent") or 0)
    if i2 >= 75:
        domains["inconsistency"] = {
            "judgment": "very_serious",
            "reason": f"I²={i2:.1f}% indica heterogeneidade substancial",
        }
    elif i2 >= 50:
        domains["inconsistency"] = {
            "judgment": "serious",
            "reason": f"I²={i2:.1f}% indica heterogeneidade moderada",
        }
    else:
        domains["inconsistency"] = {
            "judgment": "not_serious",
            "reason": f"I²={i2:.1f}% indica heterogeneidade baixa",
        }

    if any(token in body for token in ("surrogate", "indirect", "indireto")):
        domains["indirectness"] = {
            "judgment": "serious",
            "reason": "texto menciona desfecho substituto ou população indireta",
        }
    else:
        domains["indirectness"] = {
            "judgment": "not_serious",
            "reason": "nenhuma indicação textual de indirectness",
        }

    primary = meta_result.get("primary_result") or {}
    low = primary.get("ci_low")
    high = primary.get("ci_high")
    if isinstance(low, (int, float)) and isinstance(high, (int, float)):
        if low <= 0 <= high:
            domains["imprecision"] = {
                "judgment": "serious",
                "reason": "intervalo de confiança inclui o nulo",
            }
        else:
            domains["imprecision"] = {
                "judgment": "not_serious",
                "reason": "intervalo de confiança exclui o nulo",
            }
    else:
        domains["imprecision"] = {
            "judgment": "not_assessed",
            "reason": "intervalo indisponível",
        }

    k = int(meta_result.get("k") or 0)
    domains["publication_bias"] = {
        "judgment": "not_assessed",
        "reason": (
            f"apenas {k} estudos; funil não avaliável automaticamente"
            if k < 10 else "funil não avaliado automaticamente"
        ),
    }

    downgrades = 0
    for item in domains.values():
        if item["judgment"] == "serious":
            downgrades += 1
        elif item["judgment"] == "very_serious":
            downgrades += 2
    final_numeric = max(1, GRADE_ORDER[starting] - downgrades)
    return {
        "schema_version": SCHEMA_VERSION,
        "human_confirmation": True,
        "reviewer": reviewer.strip(),
        "declared_at": now(),
        "starting_level": starting,
        "domains": domains,
        "automated": True,
        "authoritative": False,
        "rule_version": RULE_VERSION,
        "human_review_required": True,
        "final_level_preview": GRADE_NAMES[final_numeric],
        "downgrades_preview": downgrades,
        "limitations": [
            "GRADE automático é uma sugestão por regras, não julgamento final.",
            "Publicação seletiva e indirectness exigem revisão humana.",
        ],
    }


def texts_by_study(
    fulltext_dir: str | Path,
    studies: list[dict],
    records: list[dict],
) -> dict[str, str]:
    index = fulltext.index_fulltexts(fulltext_dir)
    matches = fulltext.match_entries(index, studies, records)
    entries = {entry["fulltext_id"]: entry for entry in index["entries"]}
    result = {}
    for match in matches["matches"]:
        if match.get("duplicate_for_study"):
            continue
        entry = entries.get(match["fulltext_id"])
        if entry is None:
            continue
        result[match["study_id"]] = " ".join(
            page["text"] for page in entry["pages"]
        )
    return result


def write_report(out: str | Path, result: dict) -> Path:
    path = Path(out) / "04_analysis/auto-rob-grade.json"
    dump(path, result)
    return path


def enrich(
    data: dict,
    texts: dict[str, str],
    *,
    reviewer: str,
    human_confirmation: bool = False,
    out: str | Path | None = None,
) -> dict:
    if human_confirmation is not True:
        raise ValueError("enriquecimento automático exige human_confirmation=true")
    enriched = {**data, "studies": [dict(study) for study in data.get("studies", [])]}
    rob_suggestions = {}
    for study in enriched["studies"]:
        study_id = study.get("study_id")
        text = texts.get(study_id, "")
        if "risk_of_bias" not in study:
            suggestion = assess_risk_of_bias(text, study.get("design"))
            study["risk_of_bias"] = {
                "overall": suggestion["overall"],
                "domains": suggestion["domains"],
                "automated": True,
                "authoritative": False,
                "reasons": suggestion["reasons"],
            }
            rob_suggestions[study_id] = suggestion
    meta = quantitative.analyze(enriched)
    grade = assess_grade(
        meta, list(texts.values()), reviewer=reviewer,
        human_confirmation=True,
    )
    enriched["grade"] = grade
    final = quantitative.analyze(enriched)
    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "status": "automated_suggestion",
        "risk_of_bias": rob_suggestions,
        "grade": grade,
        "meta_before_grade": {
            "k": meta["k"],
            "pooled_effect": meta["primary_result"]["pooled_effect"],
            "i2": meta["heterogeneity"]["i2_percent"],
        },
        "final_meta": final,
        "truth_claim": False,
        "external_validation": False,
        "human_review_required": True,
        "limitations": [
            "As sugestões são heurísticas e não substituem RoB 2/ROBINS-I.",
            "GRADE automático não é julgamento final de certeza.",
            "O operador precisa revisar cada domínio antes de usar o resultado.",
        ],
    }
    if out is not None:
        write_report(out, report)
        dump(Path(out) / "04_analysis/quantitative-auto.json", enriched)
    return {"enriched": enriched, "report": report, "final_meta": final}
