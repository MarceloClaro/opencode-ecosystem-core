# -*- coding: utf-8 -*-
"""Validador de protocolo N-of-1 (SPEC-935-R1132).

Verifica pré-registro, desenho ABAB, washout, desfechos mínimos, cegamento,
ética e regras de parada. Não executa o estudo e não produz inferência causal;
o resumo é descritivo.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
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
