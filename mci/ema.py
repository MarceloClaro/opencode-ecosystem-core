"""R1148 — EMA auditável com compliance, dados faltantes e teste de transferência.

Medição ecológica momentânea (EMA) para separar **offloading dependente** de
**offloading autônomo**. O módulo agenda prompts, mede compliance, audita
faltantes, exige metadados psicométricos e calcula um teste de transferência
pré/pós com bootstrap.

Não substitui validação clínica, diagnóstico, ética ou supervisão. Nenhum dado
é inventado: respostas ausentes permanecem ausentes.
"""
from __future__ import annotations

import math
import random
from datetime import date, datetime, time, timedelta
from statistics import mean, median

LIMITS = (
    "EMA mede autorrelato ecológico e não substitui validação clínica, "
    "diagnóstico, ética ou supervisão. O teste de transferência é descritivo; "
    "não identifica mecanismo nem causalidade. Dados faltantes não são imputados."
)
PSYCHOMETRIC_LIMITS = (
    "Metadados psicométricos são obrigatórios, mas não provam validade no "
    "contexto local. Reliabilidade e validade devem ser reportadas com fonte."
)


def _bootstrap_mean_ci(
    values: list[float],
    *,
    n_boot: int = 2000,
    confidence: float = 0.95,
    seed: int = 0,
) -> dict:
    if len(values) < 2:
        raise ValueError("bootstrap exige ao menos dois valores")
    if not 0 < confidence < 1:
        raise ValueError("confidence deve estar em (0,1)")
    if int(n_boot) < 100:
        raise ValueError("n_boot deve ser >= 100")
    rng = random.Random(int(seed))
    n = len(values)
    means = [
        sum(values[rng.randrange(n)] for _ in range(n)) / n
        for _ in range(int(n_boot))
    ]
    means.sort()
    tail = (1.0 - confidence) / 2.0
    low = means[int(math.floor(tail * (len(means) - 1)))]
    high = means[int(math.ceil((1.0 - tail) * (len(means) - 1)))]
    return {
        "mean": float(mean(values)),
        "ci_low": float(low),
        "ci_high": float(high),
        "confidence": float(confidence),
        "n_boot": int(n_boot),
        "method": "percentil bootstrap da média",
    }


def build_schedule(
    *,
    start_date: str,
    days: int,
    prompts_per_day: int,
    seed: int = 0,
    window_minutes: int = 60,
    day_start_hour: int = 8,
    day_end_hour: int = 22,
) -> list[dict]:
    """Agenda determinística com jitter dentro de cada janela."""
    days = int(days)
    prompts_per_day = int(prompts_per_day)
    if days < 1 or prompts_per_day < 1:
        raise ValueError("days e prompts_per_day devem ser >= 1")
    if not (0 <= day_start_hour < day_end_hour <= 24):
        raise ValueError("janela diária inválida")
    if window_minutes < 0:
        raise ValueError("window_minutes deve ser >= 0")
    base = date.fromisoformat(start_date)
    rng = random.Random(int(seed))
    total_minutes = (day_end_hour - day_start_hour) * 60
    step = total_minutes / prompts_per_day
    schedule = []
    for day in range(days):
        for index in range(prompts_per_day):
            centre = day_start_hour * 60 + step * (index + 0.5)
            jitter = rng.uniform(-window_minutes / 2, window_minutes / 2)
            minute = min(max(0, centre + jitter), 24 * 60 - 1)
            moment = datetime.combine(
                base + timedelta(days=day), time(0, 0)
            ) + timedelta(minutes=minute)
            schedule.append({
                "prompt_id": f"ema-{day:02d}-{index:02d}",
                "day": day,
                "scheduled_at": moment.isoformat(timespec="minutes"),
                "window_minutes": int(window_minutes),
            })
    return schedule


def record_responses(schedule: list[dict], responses: list[dict]) -> dict:
    """Compliance e faltantes; respostas ausentes não são imputadas."""
    by_id = {slot["prompt_id"]: slot for slot in schedule}
    if len(by_id) != len(schedule):
        raise ValueError("prompt_id repetido na agenda")
    seen = set()
    supplied = {}
    for response in responses:
        prompt_id = response.get("prompt_id")
        if prompt_id not in by_id:
            raise ValueError(f"prompt_id desconhecido: {prompt_id!r}")
        if prompt_id in seen:
            raise ValueError(f"resposta duplicada: {prompt_id!r}")
        seen.add(prompt_id)
        value = response.get("value")
        answered = bool(response.get("answered", value is not None))
        if answered and value is None:
            raise ValueError(f"resposta marcada como respondida sem valor: {prompt_id!r}")
        if answered and not isinstance(value, (int, float)):
            raise ValueError(f"valor não numérico: {prompt_id!r}")
        supplied[prompt_id] = {
            "prompt_id": prompt_id,
            "day": by_id[prompt_id]["day"],
            "answered": answered,
            "value": float(value) if answered else None,
            "latency_seconds": response.get("latency_seconds"),
        }
    rows = [
        supplied.get(
            slot["prompt_id"],
            {
                "prompt_id": slot["prompt_id"],
                "day": slot["day"],
                "answered": False,
                "value": None,
                "latency_seconds": None,
            },
        )
        for slot in schedule
    ]
    answered_rows = [row for row in rows if row["answered"]]
    missing_rows = [row for row in rows if not row["answered"]]
    scheduled = len(schedule)
    compliance = len(answered_rows) / scheduled if scheduled else 0.0
    missing_by_day: dict[int, int] = {}
    answered_by_day: dict[int, int] = {}
    for row in missing_rows:
        missing_by_day[row["day"]] = missing_by_day.get(row["day"], 0) + 1
    for row in answered_rows:
        answered_by_day[row["day"]] = answered_by_day.get(row["day"], 0) + 1
    latencies = [
        float(row["latency_seconds"])
        for row in answered_rows
        if isinstance(row["latency_seconds"], (int, float))
    ]
    return {
        "schema_version": 1,
        "scheduled": scheduled,
        "answered": len(answered_rows),
        "missing": len(missing_rows),
        "compliance_rate": float(compliance),
        "missing_by_day": missing_by_day,
        "answered_by_day": answered_by_day,
        "missing_prompt_ids": [row["prompt_id"] for row in missing_rows],
        "latency_median_seconds": float(median(latencies)) if latencies else None,
        "complete_cases": len(answered_rows),
        "imputation": "none",
        "limits": LIMITS,
    }


def validate_psychometrics(metadata: dict | None) -> dict:
    """Valida metadados psicométricos obrigatórios; fail-closed."""
    if metadata is None:
        return {
            "valid": False,
            "missing": ["metadata"],
            "warnings": ["metadados psicométricos ausentes"],
            "limits": PSYCHOMETRIC_LIMITS,
        }
    missing = []
    warnings = []
    for field in ("instrument", "version", "scale", "provenance", "license"):
        if not str(metadata.get(field, "")).strip():
            missing.append(field)
    reliability = metadata.get("reliability")
    if not isinstance(reliability, dict) or not reliability:
        missing.append("reliability")
    else:
        values = [
            reliability.get("omega"),
            reliability.get("alpha"),
        ]
        values = [float(value) for value in values if value is not None]
        if not values:
            missing.append("reliability.omega|alpha")
        elif any(not 0.0 <= value <= 1.0 for value in values):
            warnings.append("reliabilidade fora de [0,1]")
        elif max(values) < 0.6:
            warnings.append("reliabilidade abaixo de 0,6")
    validity = metadata.get("validity")
    if not isinstance(validity, dict):
        missing.append("validity")
    else:
        for field in ("construct", "notes"):
            if not str(validity.get(field, "")).strip():
                missing.append(f"validity.{field}")
    return {
        "valid": not missing,
        "missing": missing,
        "warnings": warnings,
        "limits": PSYCHOMETRIC_LIMITS,
    }


def paired_transfer_test(
    baseline: list[dict],
    followup: list[dict],
    *,
    offloading_key: str = "offloading",
    autonomy_key: str = "autonomy",
    n_boot: int = 2000,
    confidence: float = 0.95,
    seed: int = 0,
) -> dict:
    """Teste pareado pré/pós: dependente vs autônomo.

    dependent: offloading sobe e autonomia cai.
    autonomous: offloading cai (ou fica igual) e autonomia sobe.
    """
    if len(baseline) != len(followup):
        raise ValueError("baseline e followup devem ter o mesmo tamanho")
    if len(baseline) < 5:
        raise ValueError("teste de transferência exige ao menos 5 pares")
    deltas_off = []
    deltas_auto = []
    for before, after in zip(baseline, followup):
        for key in (offloading_key, autonomy_key):
            if key not in before or key not in after:
                raise ValueError(f"chave ausente: {key}")
        deltas_off.append(float(after[offloading_key]) - float(before[offloading_key]))
        deltas_auto.append(float(after[autonomy_key]) - float(before[autonomy_key]))
    off = _bootstrap_mean_ci(
        deltas_off, n_boot=n_boot, confidence=confidence, seed=seed
    )
    auto = _bootstrap_mean_ci(
        deltas_auto, n_boot=n_boot, confidence=confidence, seed=seed + 1
    )
    if off["mean"] > 0 and auto["mean"] < 0:
        classification = "dependent"
    elif off["mean"] <= 0 and auto["mean"] > 0:
        classification = "autonomous"
    else:
        classification = "ambiguous"
    strong = (
        (off["ci_low"] > 0 and auto["ci_high"] < 0)
        or (off["ci_high"] < 0 and auto["ci_low"] > 0)
    )
    partial = (
        (off["ci_low"] > 0 or off["ci_high"] < 0)
        or (auto["ci_low"] > 0 or auto["ci_high"] < 0)
    )
    return {
        "schema_version": 1,
        "n_pairs": len(baseline),
        "delta_offloading": off,
        "delta_autonomy": auto,
        "classification": classification,
        "evidence_strength": "strong" if strong else "partial" if partial else "weak",
        "decision_rule": (
            "dependent: Δoffloading>0 e Δautonomia<0; "
            "autonomous: Δoffloading<=0 e Δautonomia>0; caso contrário ambiguous"
        ),
        "limits": LIMITS,
    }


def ema_report(
    *,
    schedule: list[dict],
    responses: list[dict],
    psychometrics: dict | None,
    baseline: list[dict] | None = None,
    followup: list[dict] | None = None,
    n_boot: int = 2000,
    seed: int = 0,
) -> dict:
    metadata = validate_psychometrics(psychometrics)
    compliance = record_responses(schedule, responses)
    transfer = None
    if baseline is not None and followup is not None:
        transfer = paired_transfer_test(
            baseline, followup, n_boot=n_boot, seed=seed
        )
    if not metadata["valid"]:
        status = "blocked"
    elif compliance["compliance_rate"] < 0.7:
        status = "insufficient_compliance"
    elif transfer is None:
        status = "ready_without_transfer"
    elif transfer["n_pairs"] < 5:
        status = "insufficient_transfer"
    else:
        status = "ready_for_review"
    return {
        "schema_version": 1,
        "status": status,
        "psychometrics": metadata,
        "compliance": compliance,
        "transfer": transfer,
        "limits": LIMITS,
        "clinical_validation": False,
        "hardware_executed": False,
    }
