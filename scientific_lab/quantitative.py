"""R1053-A — síntese quantitativa human-gated.

O módulo não extrai efeitos de PDFs e não decide risco de viés ou GRADE. Ele
exige um protocolo humano, dados de efeito declarados, risco de viés por estudo
e julgamentos GRADE explícitos. Sem esses insumos, o resultado é recusado.

A meta-análise implementa:
- modelo de efeitos fixos por variância inversa;
- modelo de efeitos aleatórios DerSimonian-Laird;
- Q, I², tau², H²;
- intervalo de predição (t de Student quando disponível/tabelado);
- resumo de risco de viés;
- rebaixamento GRADE por domínio, sem nota automática.
"""
from __future__ import annotations

import json
import math
import statistics
from pathlib import Path
from typing import Any, Iterable

from scientific_lab.native.common import dump, now, uid

SCHEMA_VERSION = "1.0"
EFFECT_MEASURES = {"SMD", "MD", "OR", "RR", "HR", "COR", "RD"}
MODELS = {"fixed", "random"}
RANDOM_METHODS = {"DL", "REML"}
ROB_LEVELS = {"low", "some_concerns", "high", "not_assessed"}
GRADE_LEVELS = {"high", "moderate", "low", "very_low"}
GRADE_JUDGMENTS = {"not_serious", "serious", "very_serious", "not_assessed"}
GRADE_DOMAINS = (
    "risk_of_bias", "inconsistency", "indirectness", "imprecision",
    "publication_bias",
)
GRADE_NUMERIC = {"high": 4, "moderate": 3, "low": 2, "very_low": 1}
GRADE_FROM_NUMERIC = {value: key for key, value in GRADE_NUMERIC.items()}

# t_{0.975, df} para df 1..30; acima de 30 usa 1,96 (aproximação normal).
T975 = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
    6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
    11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
    16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
    21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060,
    26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042,
}


def _finite(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} deve ser número")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} deve ser finito")
    return number


def _text(value: Any, name: str, minimum: int = 1) -> str:
    if not isinstance(value, str) or len(value.strip()) < minimum:
        raise ValueError(f"{name} deve ser texto com ao menos {minimum} caractere(s)")
    return value.strip()


def _confidence_level(protocol: dict) -> float:
    level = _finite(protocol.get("confidence_level", 0.95), "confidence_level")
    if not 0.5 < level < 1:
        raise ValueError("confidence_level deve estar entre 0.5 e 1")
    return level


def z_value(level: float) -> float:
    return statistics.NormalDist().inv_cdf(1 - (1 - level) / 2)


def t_value(df: int, level: float = 0.95) -> tuple[float, str]:
    if level != 0.95:
        try:
            from scipy.stats import t  # type: ignore
            return float(t.ppf(1 - (1 - level) / 2, df)), "scipy"
        except Exception:
            return z_value(level), "normal_approx"
    if df <= 0:
        raise ValueError("graus de liberdade inválidos")
    if df in T975:
        return T975[df], "t_table"
    return 1.96, "normal_approx"


def _protocol(data: dict) -> dict:
    protocol = data.get("protocol")
    if not isinstance(protocol, dict):
        raise ValueError("protocolo ausente")
    if protocol.get("human_confirmation") is not True:
        raise ValueError("protocolo exige human_confirmation=true")
    reviewer = _text(protocol.get("reviewer"), "reviewer", 2)
    declared_at = _text(protocol.get("declared_at"), "declared_at", 10)
    effect_measure = protocol.get("effect_measure")
    if effect_measure not in EFFECT_MEASURES:
        raise ValueError("effect_measure inválido")
    model = protocol.get("model")
    if model not in MODELS:
        raise ValueError("model deve ser fixed ou random")
    random_method = protocol.get("random_effects_method", "DL")
    if random_method not in RANDOM_METHODS:
        raise ValueError("random_effects_method deve ser DL ou REML")
    confidence = _confidence_level(protocol)
    min_studies = protocol.get("min_studies", 2)
    if isinstance(min_studies, bool) or not isinstance(min_studies, int) or min_studies < 2:
        raise ValueError("min_studies deve ser inteiro >= 2")
    max_i2 = _finite(protocol.get("max_i2_for_pooling", 75), "max_i2_for_pooling")
    if not 0 <= max_i2 <= 100:
        raise ValueError("max_i2_for_pooling deve estar em [0,100]")
    return {
        **protocol,
        "reviewer": reviewer,
        "declared_at": declared_at,
        "effect_measure": effect_measure,
        "model": model,
        "random_effects_method": random_method,
        "confidence_level": confidence,
        "min_studies": min_studies,
        "max_i2_for_pooling": max_i2,
        "heterogeneity_policy": protocol.get("heterogeneity_policy", "report_only"),
    }


def _risk_of_bias(study: dict) -> dict:
    rob = study.get("risk_of_bias")
    if not isinstance(rob, dict):
        raise ValueError(f"estudo {study.get('study_id')} sem risk_of_bias")
    overall = rob.get("overall")
    if overall not in ROB_LEVELS:
        raise ValueError(f"risk_of_bias.overall inválido em {study.get('study_id')}")
    domains = rob.get("domains")
    if not isinstance(domains, dict) or not domains:
        raise ValueError(f"risk_of_bias.domains vazio em {study.get('study_id')}")
    checked_domains = {}
    for name, judgment in domains.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("domínio de risco de viés inválido")
        if judgment not in ROB_LEVELS:
            raise ValueError(f"julgamento de risco de viés inválido: {name}")
        checked_domains[name] = judgment
    return {"overall": overall, "domains": checked_domains}


def _studies(data: dict, protocol: dict) -> list[dict]:
    studies = data.get("studies")
    if not isinstance(studies, list):
        raise ValueError("studies deve ser lista")
    if len(studies) < protocol["min_studies"]:
        raise ValueError(
            f"são necessários ao menos {protocol['min_studies']} estudos"
        )
    checked = []
    seen = set()
    for study in studies:
        if not isinstance(study, dict):
            raise ValueError("estudo deve ser objeto")
        study_id = _text(study.get("study_id"), "study_id")
        if study_id in seen:
            raise ValueError(f"study_id duplicado: {study_id}")
        seen.add(study_id)
        effect = _finite(study.get("effect_size"), f"effect_size:{study_id}")
        se = _finite(study.get("standard_error"), f"standard_error:{study_id}")
        if se <= 0:
            raise ValueError(f"standard_error deve ser > 0: {study_id}")
        checked_study = {
            "study_id": study_id,
            "label": study.get("label") or study_id,
            "effect_size": effect,
            "standard_error": se,
            "design": study.get("design"),
            "outcome": study.get("outcome"),
            "timepoint": study.get("timepoint"),
            "subgroup": study.get("subgroup"),
            "risk_of_bias": _risk_of_bias(study),
        }
        if isinstance(study.get("extraction"), dict):
            checked_study["extraction"] = study["extraction"]
        checked.append(checked_study)
    return checked


def _fixed(studies: list[dict], level: float) -> dict:
    weights = [1.0 / (study["standard_error"] ** 2) for study in studies]
    total = sum(weights)
    pooled = sum(
        weight * study["effect_size"] for weight, study in zip(weights, studies)
    ) / total
    se = math.sqrt(1.0 / total)
    z = z_value(level)
    return {
        "model": "fixed",
        "k": len(studies),
        "weights": [
            {"study_id": study["study_id"], "weight": round(weight, 6)}
            for study, weight in zip(studies, weights)
        ],
        "pooled_effect": pooled,
        "standard_error": se,
        "ci_low": pooled - z * se,
        "ci_high": pooled + z * se,
        "z": pooled / se,
        "confidence_level": level,
    }


def _dl_tau2(studies: list[dict], fixed: dict) -> float:
    weights = [1.0 / (study["standard_error"] ** 2) for study in studies]
    total = sum(weights)
    q = sum(
        weight * (study["effect_size"] - fixed["pooled_effect"]) ** 2
        for weight, study in zip(weights, studies)
    )
    df = len(studies) - 1
    c = total - sum(weight ** 2 for weight in weights) / total
    return max(0.0, (q - df) / c) if c > 0 else 0.0


def _reml_tau2(studies: list[dict]) -> tuple[float, str]:
    try:
        from scipy.optimize import minimize_scalar  # type: ignore
    except Exception:
        return _dl_tau2(studies, _fixed(studies, 0.95)), "DL_fallback"
    variances = [study["standard_error"] ** 2 for study in studies]
    effects = [study["effect_size"] for study in studies]

    def negative_reml(tau2: float) -> float:
        weights = [1.0 / (variance + tau2) for variance in variances]
        total = sum(weights)
        pooled = sum(
            weight * effect for weight, effect in zip(weights, effects)
        ) / total
        return 0.5 * (
            sum(math.log(variance + tau2) for variance in variances)
            + math.log(total)
            + sum(
                weight * (effect - pooled) ** 2
                for weight, effect in zip(weights, effects)
            )
        )

    upper = max(1.0, 10.0 * max(variances))
    try:
        result = minimize_scalar(
            negative_reml, bounds=(0.0, upper), method="bounded",
        )
        return max(0.0, float(result.x)), "REML"
    except Exception:
        return _dl_tau2(studies, _fixed(studies, 0.95)), "DL_fallback"


def _random(studies: list[dict], fixed: dict, level: float,
            method: str = "DL") -> dict:
    if method == "REML":
        tau2, method_label = _reml_tau2(studies)
    else:
        tau2, method_label = _dl_tau2(studies, fixed), "DL"
    random_weights = [
        1.0 / (study["standard_error"] ** 2 + tau2) for study in studies
    ]
    random_total = sum(random_weights)
    pooled = sum(
        weight * study["effect_size"]
        for weight, study in zip(random_weights, studies)
    ) / random_total
    se = math.sqrt(1.0 / random_total)
    z = z_value(level)
    return {
        "model": "random",
        "method": method_label,
        "k": len(studies),
        "tau2": tau2,
        "weights": [
            {"study_id": study["study_id"], "weight": round(weight, 6)}
            for study, weight in zip(studies, random_weights)
        ],
        "pooled_effect": pooled,
        "standard_error": se,
        "ci_low": pooled - z * se,
        "ci_high": pooled + z * se,
        "z": pooled / se,
        "confidence_level": level,
    }


def _heterogeneity(studies: list[dict], fixed: dict, random: dict) -> dict:
    weights = [1.0 / (study["standard_error"] ** 2) for study in studies]
    q = sum(
        weight * (study["effect_size"] - fixed["pooled_effect"]) ** 2
        for weight, study in zip(weights, studies)
    )
    df = len(studies) - 1
    i2 = max(0.0, (q - df) / q) * 100 if q > 0 else 0.0
    h2 = q / df if df > 0 else None
    p_value = None
    p_method = "not_computed"
    try:
        from scipy.stats import chi2  # type: ignore
        p_value = float(chi2.sf(q, df))
        p_method = "scipy"
    except Exception:
        pass
    return {
        "q": q,
        "df": df,
        "p_value": p_value,
        "p_value_method": p_method,
        "i2_percent": i2,
        "h2": h2,
        "tau2": random.get("tau2"),
        "interpretation": (
            "heterogeneidade substancial" if i2 >= 75
            else "heterogeneidade moderada" if i2 >= 50
            else "heterogeneidade baixa"
        ),
    }


def _prediction_interval(random: dict, k: int, level: float) -> dict:
    if k < 3:
        return {
            "status": "not_computed",
            "reason": "menos de três estudos",
            "low": None,
            "high": None,
        }
    tau2 = random.get("tau2") or 0.0
    se = math.sqrt(tau2 + random["standard_error"] ** 2)
    t, method = t_value(k - 2, level)
    return {
        "status": "computed",
        "low": random["pooled_effect"] - t * se,
        "high": random["pooled_effect"] + t * se,
        "standard_error": se,
        "t_value": t,
        "t_method": method,
        "df": k - 2,
        "confidence_level": level,
    }


def _risk_summary(studies: list[dict]) -> dict:
    overall = {}
    domains: dict[str, dict[str, int]] = {}
    for study in studies:
        rob = study["risk_of_bias"]
        overall[rob["overall"]] = overall.get(rob["overall"], 0) + 1
        for domain, judgment in rob["domains"].items():
            domains.setdefault(domain, {})
            domains[domain][judgment] = domains[domain].get(judgment, 0) + 1
    return {
        "overall_counts": overall,
        "domain_counts": domains,
        "studies_with_high_risk": sum(
            study["risk_of_bias"]["overall"] == "high" for study in studies
        ),
        "policy": "human_judgment_only_no_automatic_score",
        "truth_claim": False,
    }


def _grade(data: dict) -> dict:
    grade = data.get("grade")
    if grade is None:
        return {
            "status": "not_assessed",
            "final_level": None,
            "reason": "julgamento GRADE não fornecido",
            "human_review_required": True,
        }
    if not isinstance(grade, dict):
        raise ValueError("grade deve ser objeto")
    if grade.get("human_confirmation") is not True:
        raise ValueError("grade exige human_confirmation=true")
    reviewer = _text(grade.get("reviewer"), "grade.reviewer", 2)
    declared_at = _text(grade.get("declared_at"), "grade.declared_at", 10)
    starting = grade.get("starting_level")
    if starting not in GRADE_LEVELS:
        raise ValueError("grade.starting_level inválido")
    domains = grade.get("domains")
    if not isinstance(domains, dict):
        raise ValueError("grade.domains deve ser objeto")
    checked = {}
    downgrades = 0
    for domain in GRADE_DOMAINS:
        item = domains.get(domain)
        if not isinstance(item, dict):
            raise ValueError(f"grade.domains.{domain} ausente")
        judgment = item.get("judgment")
        if judgment not in GRADE_JUDGMENTS:
            raise ValueError(f"grade.domains.{domain}.judgment inválido")
        reason = item.get("reason")
        if judgment in {"serious", "very_serious"}:
            _text(reason, f"grade.domains.{domain}.reason", 10)
        if judgment == "serious":
            downgrades += 1
        elif judgment == "very_serious":
            downgrades += 2
        checked[domain] = {"judgment": judgment, "reason": reason}
    final_numeric = max(1, GRADE_NUMERIC[starting] - downgrades)
    return {
        "status": "assessed",
        "outcome": grade.get("outcome"),
        "starting_level": starting,
        "downgrades": downgrades,
        "final_level": GRADE_FROM_NUMERIC[final_numeric],
        "domains": checked,
        "reviewer": reviewer,
        "declared_at": declared_at,
        "automated": grade.get("automated", False),
        "authoritative": False,
        "policy": "human_judgment_only_no_automatic_certainty",
        "truth_claim": False,
        "human_review_required": True,
    }


def analyze(data: dict) -> dict:
    if not isinstance(data, dict):
        raise ValueError("dados devem ser objeto")
    protocol = _protocol(data)
    studies = _studies(data, protocol)
    level = protocol["confidence_level"]
    fixed = _fixed(studies, level)
    random = _random(
        studies, fixed, level, protocol["random_effects_method"],
    )
    heterogeneity = _heterogeneity(studies, fixed, random)
    prediction = _prediction_interval(random, len(studies), level)
    risk = _risk_summary(studies)
    grade = _grade(data)
    primary = random if protocol["model"] == "random" else fixed
    caution = []
    if heterogeneity["i2_percent"] > protocol["max_i2_for_pooling"]:
        caution.append(
            "I² acima do limite declarado para pooling; interprete com cautela."
        )
    if risk["studies_with_high_risk"]:
        caution.append("Há estudo(s) com risco de viés alto.")
    if grade["status"] != "assessed":
        caution.append("GRADE não foi avaliado por humano.")
    automated = protocol.get("automated_extraction") is True
    limitations = [
        "A meta-análise usa apenas os efeitos e erros declarados pelo operador.",
        "Não houve extração automática de PDFs nem imputação de dados faltantes.",
        "Risco de viés e GRADE são julgamentos humanos registrados, não notas automáticas.",
        "O resultado não é verdade científica nem validação externa.",
    ]
    if automated:
        limitations[0] = (
            "Efeitos extraídos automaticamente por regex; revisão humana obrigatória."
        )
        limitations[1] = (
            "A extração automática não foi validada por dois revisores independentes."
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "analysis_id": uid("QUANT", 12),
        "project_id": data.get("project_id"),
        "generated_at": now(),
        "status": "completed",
        "protocol": protocol,
        "k": len(studies),
        "studies": studies,
        "fixed": fixed,
        "random": random,
        "primary_model": protocol["model"],
        "primary_result": primary,
        "heterogeneity": heterogeneity,
        "prediction_interval": prediction,
        "risk_of_bias": risk,
        "grade": grade,
        "caution": caution,
        "pooling_warning": bool(caution),
        "automated_extraction": automated,
        "extraction_origin": "automated" if automated else "declared",
        "truth_claim": False,
        "external_validation": False,
        "human_review_required": True,
        "limitations": limitations,
    }


def load_data(path: str | Path) -> dict:
    data_path = Path(path)
    if not data_path.exists():
        raise ValueError(f"dados quantitativos não encontrados: {data_path}")
    if data_path.stat().st_size > 2_000_000:
        raise ValueError("dados quantitativos excedem 2 MB")
    try:
        data = json.loads(data_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"dados quantitativos ilegíveis: {type(exc).__name__}") from exc
    return data


def run(path: str | Path, out: str | Path) -> dict:
    result = analyze(load_data(path))
    dump(Path(out) / "04_analysis/quantitative-synthesis.json", result)
    return result


def summary(result: dict) -> dict:
    primary = result["primary_result"]
    return {
        "status": result["status"],
        "k": result["k"],
        "model": result["primary_model"],
        "pooled_effect": primary["pooled_effect"],
        "ci_low": primary["ci_low"],
        "ci_high": primary["ci_high"],
        "i2_percent": result["heterogeneity"]["i2_percent"],
        "q": result["heterogeneity"]["q"],
        "tau2": result["heterogeneity"]["tau2"],
        "prediction_interval": result["prediction_interval"],
        "grade": result["grade"].get("final_level"),
        "risk_of_bias_high": result["risk_of_bias"]["studies_with_high_risk"],
        "truth_claim": False,
        "external_validation": False,
        "human_review_required": True,
    }
