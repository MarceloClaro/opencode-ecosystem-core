# -*- coding: utf-8 -*-
"""N-of-1 canônico: validador de protocolo e runner/SCED (R1132/R1148/R1150).

Verifica pré-registro, desenho ABAB, washout, desfechos mínimos, cegamento,
ética e regras de parada; também executa o runner com randomização por blocos,
lock SHA-256, adesão, eventos adversos e análise SCED (NAP, PEM, Tau-U,
autocorrelação e permutação).

Não executa o estudo com participantes e não produz inferência causal; o resumo
é descritivo. Exige ética, consentimento e supervisão.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean, median
from typing import Any

REQUIRED_OUTCOMES = frozenset(
    {
        "time_to_resume",
        "task_completion",
        "errors",
        "cognitive_load",
        "trust_calibration",
        "agency",
        "sleep_social",
        "stress",
    }
)
_REQUIRED_ETHICS = ("consent", "clinical_oversight", "data_protection")


@dataclass(frozen=True)
class Protocol:
    title: str
    hypothesis: str
    design: str
    outcomes: list[str]
    randomization: bool
    blinding: bool
    pre_registration: bool
    ethics: dict[str, Any]
    stopping_rules: list[str]
    duration_weeks: int
    washout_weeks: int
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} deve ser texto não vazio")
    return value.strip()


def _bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field} deve ser booleano")
    return value


def validate_protocol(data: dict[str, Any]) -> Protocol:
    if not isinstance(data, dict):
        raise ValueError("protocolo deve ser um objeto")

    title = _text(data.get("title"), "title")
    hypothesis = _text(data.get("hypothesis"), "hypothesis")
    design = _text(data.get("design"), "design")
    normalized_design = "".join(ch for ch in design.lower() if ch.isalnum())
    if "abab" not in normalized_design:
        raise ValueError("design deve explicitar ABAB")

    outcomes = data.get("outcomes")
    if not isinstance(outcomes, list) or any(not isinstance(item, str) for item in outcomes):
        raise ValueError("outcomes deve ser lista de textos")
    outcomes = [item.strip() for item in outcomes if item.strip()]
    if len(set(outcomes)) < 5:
        raise ValueError("pelo menos cinco desfechos distintos são obrigatórios")
    if len(REQUIRED_OUTCOMES - set(outcomes)) > 3:
        raise ValueError(
            "desfechos obrigatórios insuficientes; inclua pelo menos cinco de "
            f"{sorted(REQUIRED_OUTCOMES)}"
        )

    randomization = _bool(data.get("randomization"), "randomization")
    blinding = _bool(data.get("blinding"), "blinding")
    pre_registration = _bool(data.get("pre_registration"), "pre_registration")
    if not (randomization and blinding and pre_registration):
        raise ValueError("randomization, blinding e pre_registration devem ser true")

    ethics = data.get("ethics")
    if not isinstance(ethics, dict):
        raise ValueError("ethics deve ser um objeto")
    missing_ethics = [key for key in _REQUIRED_ETHICS if ethics.get(key) is not True]
    if missing_ethics:
        raise ValueError(f"ethics incompleto: {missing_ethics}")

    stopping_rules = data.get("stopping_rules")
    if not isinstance(stopping_rules, list) or not stopping_rules:
        raise ValueError("stopping_rules deve ser lista não vazia")
    if any(not isinstance(item, str) or not item.strip() for item in stopping_rules):
        raise ValueError("stopping_rules deve conter textos não vazios")

    duration = data.get("duration_weeks")
    washout = data.get("washout_weeks")
    if isinstance(duration, bool) or not isinstance(duration, int) or duration < 8:
        raise ValueError("duration_weeks deve ser inteiro >= 8")
    if isinstance(washout, bool) or not isinstance(washout, int) or washout < 0:
        raise ValueError("washout_weeks deve ser inteiro >= 0")

    notes = data.get("notes", "")
    if not isinstance(notes, str):
        raise ValueError("notes deve ser texto")

    return Protocol(
        title=title,
        hypothesis=hypothesis,
        design=design,
        outcomes=outcomes,
        randomization=randomization,
        blinding=blinding,
        pre_registration=pre_registration,
        ethics=dict(ethics),
        stopping_rules=[item.strip() for item in stopping_rules],
        duration_weeks=duration,
        washout_weeks=washout,
        notes=notes.strip(),
    )


def template() -> dict[str, Any]:
    return {
        "title": "Protocolo N-of-1 para avaliar a prótese cognitiva",
        "hypothesis": (
            "O uso do Core reduz o custo de retomada e melhora a calibração da "
            "confiança sem aumentar a carga cognitiva percebida."
        ),
        "design": "ABAB com blocos randomizados ao longo de 12 semanas",
        "outcomes": [
            "time_to_resume",
            "task_completion",
            "errors",
            "cognitive_load",
            "trust_calibration",
            "agency",
            "sleep_social",
            "stress",
        ],
        "randomization": True,
        "blinding": True,
        "pre_registration": True,
        "ethics": {
            "consent": True,
            "clinical_oversight": True,
            "data_protection": True,
        },
        "stopping_rules": [
            "Parar se houver sinal de declínio cognitivo ou sofrimento significativo.",
            "Parar se o participante solicitar retirada.",
            "Parar se a carga de manutenção superar o benefício percebido por duas semanas.",
        ],
        "duration_weeks": 12,
        "washout_weeks": 1,
        "notes": "Protocolo descritivo; não é estudo executado nem alegação de eficácia.",
    }


def write_template(path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(template(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return target


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Resumo descritivo por desfecho e fase; não é teste de efeito."""

    if not isinstance(rows, list) or not rows:
        raise ValueError("rows deve ser lista não vazia")
    grouped: dict[str, dict[str, list[float]]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("cada linha deve ser um objeto")
        outcome = row.get("outcome")
        phase = row.get("phase")
        value = row.get("value")
        if not isinstance(outcome, str) or not outcome.strip():
            raise ValueError("outcome deve ser texto")
        if phase not in {"A", "B"}:
            raise ValueError("phase deve ser 'A' ou 'B'")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("value deve ser numérico")
        grouped.setdefault(outcome, {"A": [], "B": []})[phase].append(float(value))

    result: dict[str, Any] = {}
    for outcome, phases in sorted(grouped.items()):
        a_values = phases["A"]
        b_values = phases["B"]
        if not a_values or not b_values:
            raise ValueError(f"outcome {outcome} precisa de valores em A e B")
        mean_a = sum(a_values) / len(a_values)
        mean_b = sum(b_values) / len(b_values)
        result[outcome] = {
            "n_A": len(a_values),
            "n_B": len(b_values),
            "mean_A": round(mean_a, 6),
            "mean_B": round(mean_b, 6),
            "delta_B_minus_A": round(mean_b - mean_a, 6),
        }
    return {
        "descriptive_only": True,
        "outcomes": result,
    }


LIMITS = (
    "N-of-1 é um desenho de caso único; não prova eficácia populacional, "
    "causalidade universal ou generalização. Exige participante, consentimento, "
    "ética e supervisão. Autocorrelação e poucas fases limitam a inferência."
)
SCED_LIMITS = (
    "NAP, PEM e Tau-U são medidas de não sobreposição; Tau-U usa correção "
    "simplificada de tendência de Parker e não substitui randomização, "
    "modelagem ou revisão especializada."
)
REQUIRED_PROTOCOL = (
    "protocol_id",
    "phases",
    "primary_outcome",
    "randomization",
    "seed",
    "analysis_plan",
    "stopping_rule",
    "ethics",
)


def _canonical(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def generate_sequence(phases: list[dict], *, seed: int = 0, block_size: int = 2) -> list[str]:
    """Sequência balanceada por blocos; o seed é registrado no protocolo."""
    if not phases:
        raise ValueError("phases não pode ser vazio")
    if int(block_size) < 1:
        raise ValueError("block_size deve ser >= 1")
    labels = []
    for phase in phases:
        name = str(phase.get("name", "")).strip()
        count = int(phase.get("n", 0))
        if not name or count < 1:
            raise ValueError("cada fase exige name e n >= 1")
        labels.extend([name] * count)
    rng = random.Random(int(seed))
    block = int(block_size)
    for start in range(0, len(labels), block):
        chunk = labels[start:start + block]
        rng.shuffle(chunk)
        labels[start:start + block] = chunk
    return labels


def lock_preregistration(protocol: dict) -> dict:
    """Congela o protocolo e devolve SHA-256 canônico."""
    missing = [field for field in REQUIRED_PROTOCOL if not protocol.get(field)]
    if missing:
        raise ValueError(f"protocolo incompleto: {missing}")
    phases = protocol.get("phases")
    if not isinstance(phases, list) or len(phases) < 2:
        raise ValueError("protocolo exige ao menos duas fases")
    canonical = _canonical(protocol)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return {
        "locked": True,
        "hash": digest,
        "canonical": canonical,
        "protocol": protocol,
    }


def verify_lock(protocol: dict, expected_hash: str) -> bool:
    return (
        hashlib.sha256(_canonical(protocol).encode("utf-8")).hexdigest()
        == str(expected_hash)
    )


def _sign(value: float) -> int:
    return (value > 0) - (value < 0)


def nap(baseline: list[float], treatment: list[float], *, direction: str = "increase") -> float:
    if not baseline or not treatment:
        raise ValueError("fases vazias")
    if direction not in ("increase", "decrease"):
        raise ValueError("direction deve ser increase ou decrease")
    factor = 1.0 if direction == "increase" else -1.0
    wins = 0.0
    total = 0
    for before in baseline:
        for after in treatment:
            total += 1
            delta = factor * (after - before)
            if delta > 0:
                wins += 1.0
            elif delta == 0:
                wins += 0.5
    return wins / total


def pem(baseline: list[float], treatment: list[float], *, direction: str = "increase") -> float:
    if not baseline or not treatment:
        raise ValueError("fases vazias")
    if direction not in ("increase", "decrease"):
        raise ValueError("direction deve ser increase ou decrease")
    centre = median(baseline)
    if direction == "increase":
        count = sum(1 for value in treatment if value > centre)
    else:
        count = sum(1 for value in treatment if value < centre)
    return count / len(treatment)


def tau_u(
    baseline: list[float],
    treatment: list[float],
    *,
    direction: str = "increase",
) -> dict:
    """Tau-U com correção simplificada de tendência da linha de base."""
    if len(baseline) < 2 or not treatment:
        raise ValueError("Tau-U exige baseline >= 2 e tratamento não vazio")
    if direction not in ("increase", "decrease"):
        raise ValueError("direction deve ser increase ou decrease")
    factor = 1.0 if direction == "increase" else -1.0
    base = [factor * value for value in baseline]
    treat = [factor * value for value in treatment]
    s_ab = sum(_sign(after - before) for before in base for after in treat)
    tau_ab = s_ab / (len(base) * len(treat))
    pairs = len(base) * (len(base) - 1) / 2
    s_trend = sum(
        _sign(base[right] - base[left])
        for left in range(len(base))
        for right in range(left + 1, len(base))
    )
    tau_trend = s_trend / pairs if pairs else 0.0
    combined = max(-1.0, min(1.0, tau_ab - tau_trend))
    return {
        "tau_ab": float(tau_ab),
        "tau_baseline_trend": float(tau_trend),
        "tau_u": float(combined),
        "formula": "tau_ab - tau_trend (Parker, simplificado)",
        "limits": SCED_LIMITS,
    }


def lag1_autocorrelation(values: list[float]) -> float:
    if len(values) < 3:
        return 0.0
    left = values[:-1]
    right = values[1:]
    mean_left = mean(left)
    mean_right = mean(right)
    numerator = sum(
        (a - mean_left) * (b - mean_right) for a, b in zip(left, right)
    )
    denominator = math.sqrt(
        sum((a - mean_left) ** 2 for a in left)
        * sum((b - mean_right) ** 2 for b in right)
    )
    if denominator == 0:
        return 0.0
    return float(numerator / denominator)


def permutation_test_nap(
    baseline: list[float],
    treatment: list[float],
    *,
    direction: str = "increase",
    n_permutations: int = 2000,
    seed: int = 0,
) -> dict:
    if int(n_permutations) < 100:
        raise ValueError("n_permutations deve ser >= 100")
    observed = nap(baseline, treatment, direction=direction)
    combined = list(baseline) + list(treatment)
    rng = random.Random(int(seed))
    count = 0
    for _ in range(int(n_permutations)):
        rng.shuffle(combined)
        permuted_baseline = combined[:len(baseline)]
        permuted_treatment = combined[len(baseline):]
        if nap(permuted_baseline, permuted_treatment, direction=direction) >= observed - 1e-12:
            count += 1
    return {
        "observed_nap": float(observed),
        "p_value_one_sided": float((count + 1) / (int(n_permutations) + 1)),
        "n_permutations": int(n_permutations),
        "method": "permutação de rótulos de fase",
        "limits": SCED_LIMITS,
    }


def run_n_of_1(
    protocol: dict,
    observations: list[dict],
    expected_hash: str,
    *,
    direction: str = "increase",
    n_permutations: int = 2000,
    seed: int = 0,
) -> dict:
    if not verify_lock(protocol, expected_hash):
        return {
            "schema_version": 1,
            "status": "lock_mismatch",
            "analyzed": False,
            "limits": LIMITS,
            "hardware_executed": False,
        }
    phase_names = {str(phase["name"]) for phase in protocol["phases"]}
    rows = []
    for observation in observations:
        phase = str(observation.get("phase", "")).strip()
        if phase not in phase_names:
            raise ValueError(f"fase desconhecida: {phase!r}")
        value = observation.get("value")
        if not isinstance(value, (int, float)):
            raise ValueError(f"valor não numérico na fase {phase!r}")
        rows.append({
            "phase": phase,
            "value": float(value),
            "adherence": bool(observation.get("adherence", True)),
            "adverse_event": observation.get("adverse_event"),
        })
    adverse = []
    for row in rows:
        event = row["adverse_event"]
        if isinstance(event, dict):
            adverse.append(event)
        elif event:
            adverse.append({"severity": str(event)})
    severe = [
        event for event in adverse
        if str(event.get("severity", "")).lower() in {"severe", "life_threatening"}
    ]
    adherence_rate = (
        sum(1 for row in rows if row["adherence"]) / len(rows) if rows else 0.0
    )
    if severe:
        return {
            "schema_version": 1,
            "status": "halted_adverse_event",
            "analyzed": False,
            "adherence_rate": adherence_rate,
            "adverse_events": adverse,
            "severe_events": severe,
            "limits": LIMITS,
            "hardware_executed": False,
        }
    baseline = [
        row["value"] for row in rows if "baseline" in row["phase"].lower()
    ]
    treatment = [
        row["value"] for row in rows if "baseline" not in row["phase"].lower()
    ]
    if len(baseline) < 3 or len(treatment) < 3:
        return {
            "schema_version": 1,
            "status": "insufficient_data",
            "analyzed": False,
            "n_baseline": len(baseline),
            "n_treatment": len(treatment),
            "adherence_rate": adherence_rate,
            "adverse_events": adverse,
            "limits": LIMITS,
            "hardware_executed": False,
        }
    metrics = {
        "nap": nap(baseline, treatment, direction=direction),
        "pem": pem(baseline, treatment, direction=direction),
        "tau_u": tau_u(baseline, treatment, direction=direction),
        "autocorrelation_lag1": lag1_autocorrelation(
            [row["value"] for row in rows]
        ),
        "permutation": permutation_test_nap(
            baseline,
            treatment,
            direction=direction,
            n_permutations=n_permutations,
            seed=seed,
        ),
    }
    warnings = []
    if abs(metrics["autocorrelation_lag1"]) > 0.3:
        warnings.append("autocorrelação |rho| > 0,3; inferência pode ser frágil")
    if adherence_rate < 0.8:
        warnings.append("adesão < 0,8; interpretar com cautela")
    if len(baseline) < 5 or len(treatment) < 5:
        warnings.append("menos de 5 observações por fase")
    return {
        "schema_version": 1,
        "status": "analyzed",
        "analyzed": True,
        "n_baseline": len(baseline),
        "n_treatment": len(treatment),
        "adherence_rate": adherence_rate,
        "adverse_events": adverse,
        "metrics": metrics,
        "warnings": warnings,
        "direction": direction,
        "limits": f"{LIMITS} {SCED_LIMITS}",
        "hardware_executed": False,
    }
