"""R1054 — validação numérica contra uma meta-análise publicada.

O benchmark usa o dataset BCG (13 ensaios; Colditz et al. 1994) e compara o
modelo REML do Core com uma reanálise pública REML. É uma validação numérica,
não uma validação clínica, editorial ou externa.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from scientific_lab import quantitative
from scientific_lab.native.common import dump, now, uid

SCHEMA_VERSION = "1.0"


def load_bcg(path: str | Path) -> list[dict]:
    csv_path = Path(path)
    if not csv_path.exists():
        raise ValueError(f"dataset BCG não encontrado: {csv_path}")
    studies = []
    with csv_path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            try:
                a, b = int(row["tpos"]), int(row["tneg"])
                c, d = int(row["cpos"]), int(row["cneg"])
            except (KeyError, ValueError) as exc:
                raise ValueError("linha BCG inválida") from exc
            if min(a, b, c, d) <= 0:
                raise ValueError("contagem BCG deve ser positiva")
            log_or = math.log((a * d) / (b * c))
            se = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
            allocation = (row.get("alloc") or "").strip().lower()
            overall = "some_concerns" if allocation == "random" else "high"
            studies.append({
                "study_id": row.get("trial") or row.get("author"),
                "label": row.get("author"),
                "effect_size": log_or,
                "standard_error": se,
                "design": "RCT",
                "outcome": "tuberculose",
                "risk_of_bias": {
                    "overall": overall,
                    "domains": {"randomization": overall},
                },
                "allocation": allocation,
            })
    if len(studies) < 3:
        raise ValueError("dataset BCG deve ter ao menos três estudos")
    return studies


def _diff(observed: float, reference: float) -> float:
    return abs(float(observed) - float(reference))


def run(
    csv_path: str | Path,
    reference_path: str | Path,
    *,
    out: str | Path | None = None,
) -> dict:
    reference_doc = json.loads(Path(reference_path).read_text(encoding="utf-8"))
    reference = reference_doc["reference"]
    tolerances = reference_doc["tolerances"]
    studies = load_bcg(csv_path)
    data = {
        "project_id": "RP-BCG-BENCHMARK",
        "protocol": {
            "reviewer": "R1054 benchmark",
            "declared_at": now(),
            "effect_measure": "OR",
            "model": "random",
            "random_effects_method": "REML",
            "confidence_level": 0.95,
            "min_studies": 3,
            "max_i2_for_pooling": 100,
            "human_confirmation": True,
        },
        "studies": studies,
    }
    result = quantitative.analyze(data)
    random = result["random"]
    heterogeneity = result["heterogeneity"]
    observed = {
        "k": result["k"],
        "pooled_log_or": random["pooled_effect"],
        "pooled_or": math.exp(random["pooled_effect"]),
        "ci_low": math.exp(random["ci_low"]),
        "ci_high": math.exp(random["ci_high"]),
        "tau2": random["tau2"],
        "q": heterogeneity["q"],
        "df": heterogeneity["df"],
        "i2_standard": heterogeneity["i2_percent"],
        "random_method": random.get("method"),
    }
    checks = []

    def check(name: str, observed_value: Any, reference_value: Any, tolerance: float):
        if isinstance(observed_value, (int, float)) and isinstance(reference_value, (int, float)):
            difference = _diff(observed_value, reference_value)
            ok = difference <= tolerance
            checks.append({
                "id": name,
                "status": "pass" if ok else "fail",
                "observed": observed_value,
                "reference": reference_value,
                "difference": difference,
                "tolerance": tolerance,
            })
        else:
            ok = observed_value == reference_value
            checks.append({
                "id": name,
                "status": "pass" if ok else "fail",
                "observed": observed_value,
                "reference": reference_value,
            })

    check("k", observed["k"], reference["k"], 0)
    check("pooled_log_or", observed["pooled_log_or"], reference["pooled_log_or"],
          tolerances["pooled_log_or"])
    check("pooled_or", observed["pooled_or"], reference["pooled_or"],
          tolerances["pooled_or"])
    check("ci_low", observed["ci_low"], reference["ci_low"], tolerances["ci"])
    check("ci_high", observed["ci_high"], reference["ci_high"], tolerances["ci"])
    check("tau2", observed["tau2"], reference["tau2"], tolerances["tau2"])
    check("q", observed["q"], reference["q"], tolerances["q"])
    check("i2_standard", observed["i2_standard"], reference["standard_i2_from_q"],
          tolerances["i2_standard"])
    check("i2_published", observed["i2_standard"], reference["published_i2"],
          tolerances["i2_published"])
    checks.append({
        "id": "random_method",
        "status": "pass" if observed["random_method"] == "REML" else "fail",
        "observed": observed["random_method"],
        "reference": "REML",
    })
    status = "pass" if all(item["status"] == "pass" for item in checks) else "fail"
    result_doc = {
        "schema_version": SCHEMA_VERSION,
        "benchmark_id": "R1054-BCG",
        "generated_at": now(),
        "status": status,
        "dataset": reference_doc.get("dataset"),
        "csv_sha256": hashlib.sha256(
            Path(csv_path).read_bytes()
        ).hexdigest(),
        "reference_method": reference_doc.get("reference_method"),
        "observed": observed,
        "reference": reference,
        "checks": checks,
        "differences": {
            "pooled_or": _diff(observed["pooled_or"], reference["pooled_or"]),
            "tau2": _diff(observed["tau2"], reference["tau2"]),
            "q": _diff(observed["q"], reference["q"]),
            "i2_published": _diff(
                observed["i2_standard"], reference["published_i2"],
            ),
        },
        "source_urls": reference_doc.get("source_urls", []),
        "notes": reference_doc.get("notes", []),
        "truth_claim": False,
        "external_validation": False,
        "human_review_required": True,
        "limitations": [
            "Validação numérica de um dataset público, não validação clínica.",
            "A referência é uma reanálise REML pública, não o texto original de 1994.",
            "O I² publicado difere ligeiramente da fórmula (Q-df)/Q; a discrepância é registrada.",
            "O benchmark não testa extração de PDF, risco de viés ou GRADE.",
        ],
    }
    if out is not None:
        dump(Path(out) / "04_analysis/real-meta-benchmark.json", result_doc)
    return result_doc
