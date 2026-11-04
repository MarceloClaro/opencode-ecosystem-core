"""R1050: gate metacognitivo que impede confiança de virar verdade.

Combina evidência literal, calibração, contradições, falseabilidade e validação
externa. Nenhum voto, nota ou payoff promove um claim a verdade.
"""
from __future__ import annotations

import math
import re
from typing import Any

HEX = re.compile(r"[0-9a-f]{64}\Z")
INFERENCE_LEVELS = {"observation", "inference", "hypothesis"}


def _number(value, low=0.0, high=1.0):
    if isinstance(value, bool) or not isinstance(value, (int, float)) \
            or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f"número deve estar em [{low}, {high}]")
    return float(value)


def _text(value, limit=4000):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError("texto obrigatório ou excessivo")
    return value.strip()


def _evidence(items):
    if not isinstance(items, list) or not items:
        return []
    checked = []
    for item in items:
        if not isinstance(item, dict) or set(item) != {
                "source_id", "quote", "source_sha256", "literal_verified"}:
            raise ValueError("evidência deve conter source_id, quote, source_sha256 e literal_verified")
        if item["literal_verified"] is not True:
            raise ValueError("evidência não verificada literalmente")
        if not isinstance(item["source_sha256"], str) or not HEX.fullmatch(item["source_sha256"]):
            raise ValueError("hash da fonte inválido")
        checked.append({"source_id": _text(item["source_id"], 100),
                        "quote": _text(item["quote"], 2000),
                        "source_sha256": item["source_sha256"],
                        "literal_verified": True})
    return checked


def _external(value):
    if value is None:
        return False
    if not isinstance(value, dict):
        raise ValueError("validação externa inválida")
    return (value.get("independent") is True
            and isinstance(value.get("verifier"), str) and bool(value["verifier"].strip())
            and isinstance(value.get("artifact_sha256"), str)
            and bool(HEX.fullmatch(value["artifact_sha256"])))


def evaluate_claim(claim: dict, *, external_validation: dict | None = None,
                   calibration: dict | None = None) -> dict:
    if not isinstance(claim, dict):
        raise ValueError("claim deve ser objeto")
    required = {"id", "text", "confidence", "evidence", "inference_level",
                "falsifier", "contradictions", "mechanism"}
    missing = required - set(claim)
    if missing:
        raise ValueError(f"claim incompleto: {sorted(missing)}")
    claim_id = _text(claim["id"], 100)
    _text(claim["text"], 4000)
    confidence = _number(claim["confidence"])
    if claim["inference_level"] not in INFERENCE_LEVELS:
        raise ValueError("inference_level inválido")
    if not isinstance(claim["falsifier"], str) or not claim["falsifier"].strip():
        return _result(claim_id, "blocked", confidence, ["missing_falsifier"], [], False,
                       "Um claim sem critério de refutação não entra.")
    evidence = _evidence(claim["evidence"])
    contradictions = claim["contradictions"]
    if not isinstance(contradictions, list) or any(not isinstance(x, str) for x in contradictions):
        raise ValueError("contradições devem ser lista de textos")
    mechanism = _text(claim["mechanism"], 2000)
    if claim["inference_level"] in {"inference", "hypothesis"} and len(mechanism) < 20:
        return _result(claim_id, "partial", confidence,
                       ["inference_without_mechanism"], evidence, False,
                       "Inferência ou hipótese exige mecanismo declarado.")
    sources = {item["source_id"] for item in evidence}
    checks = {
        "has_evidence": bool(evidence),
        "independent_evidence": len(sources) >= 2,
        "contradictions_resolved_not_asserted": not contradictions,
        "inference_level": claim["inference_level"],
        "mechanism_declared": len(mechanism) >= 20,
        "external_validation": _external(external_validation),
        "calibration": calibration,
    }
    reasons = []
    if not evidence:
        reasons.append("no_literal_evidence")
    if confidence >= 0.8 and len(sources) < 2:
        reasons.append("high_confidence_requires_two_independent_sources")
    if contradictions:
        reasons.append("unresolved_contradictions")
    if calibration is not None:
        if not isinstance(calibration, dict):
            raise ValueError("calibração inválida")
        brier = calibration.get("brier")
        samples = calibration.get("samples", 0)
        if brier is not None:
            _number(brier)
        if type(samples) is not int or samples < 0:
            raise ValueError("amostras de calibração inválidas")
        if samples >= 5 and brier is not None and brier > 0.25:
            reasons.append("calibration_brier_above_0.25")
    if not evidence:
        status = "blocked"
    elif reasons:
        status = "partial"
    elif checks["external_validation"]:
        status = "externally_supported"
    else:
        status = "candidate"
    return _result(claim_id, status, confidence, reasons, evidence,
                   checks["external_validation"], None, checks)


def _result(claim_id, status, confidence, reasons, evidence, external, limitation,
            checks=None):
    return {
        "claim_id": claim_id,
        "status": status,
        "confidence": confidence,
        "truth_claim": False,
        "external_validation": bool(external),
        "reasons": reasons,
        "checks": checks or {},
        "evidence_count": len(evidence),
        "independent_sources": len({e["source_id"] for e in evidence}),
        "limitation": limitation or (
            "Status externamente suportado não é verdade absoluta; "
            "voto, nota e payoff não promovem claims."),
        "human_review_required": True,
    }


def aggregate(claims: list[dict], *, external_validation=None,
              calibration=None) -> dict:
    if not isinstance(claims, list) or not 1 <= len(claims) <= 50:
        raise ValueError("lista de claims deve ter 1..50")
    results = [evaluate_claim(c, external_validation=external_validation,
                              calibration=calibration) for c in claims]
    statuses = [r["status"] for r in results]
    if "blocked" in statuses:
        status = "blocked"
    elif "partial" in statuses:
        status = "partial"
    elif all(s == "externally_supported" for s in statuses):
        status = "externally_supported"
    else:
        status = "candidate"
    return {
        "status": status,
        "truth_claim": False,
        "claims": results,
        "counts": {s: statuses.count(s) for s in sorted(set(statuses))},
        "policy": "vote_score_payoff_never_truth",
        "confidence_promoted": False,
        "human_review_required": True,
    }
