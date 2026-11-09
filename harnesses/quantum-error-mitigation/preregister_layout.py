#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pré-registro de n e gates para comparação de layouts (R1120).

Lê as evidências atuais, calcula n para meia-largura pré-registrada e emite
uma decisão explícita. Não executa hardware.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from quantum_mitigation import preregister_ci

BASE = Path(__file__).resolve().parent / "resultados"
Q0 = BASE / "hardware_tomography_q0" / "comparison.json"
Q1 = BASE / "hardware_tomography_q1" / "comparison.json"
COMPARISON = BASE / "comparison_q0_q1.json"
READOUT = (
    RAIZ
    / "harnesses"
    / "gjq-hardware-optimizers"
    / "resultados"
    / "baihua"
    / "E05_comparacao"
    / "comparacao.json"
)
OUT = BASE / "preregistration_layout.json"
REPORT = BASE / "RELATORIO_PREREGISTRO.md"

COHERENCE_GATE = 0.99
R1_GATE = 0.05
LAYOUT_EFFECT_GATE = 0.01
CONFIDENCE = 0.95
P_PLANNING = 0.5
HALF_WIDTHS = (0.005, 0.01, 0.015)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _tomography_evidence(payload: dict) -> dict:
    fit = payload["fit_combined"]
    fidelity = fit["prep_fidelity"]
    return {
        "n_sets": payload["n_sets"],
        "coherence_prep": min(fidelity["+"], fidelity["+i"]),
        "r0": fit["readout_p1_given_prep0"],
        "r1": fit["readout_p0_given_prep1"],
    }


def _mitigated(case: dict) -> float:
    value = case.get("mitigated_tvd_vs_ideal")
    if value is None:
        value = case.get("mitigated_tvd_subspace")
    if value is None:
        raise KeyError("caso sem mitigated_tvd_vs_ideal/mitigated_tvd_subspace")
    return float(value)


def _readout_evidence(payload: dict) -> dict:
    baseline = _mitigated(payload["baseline"])
    optimized = _mitigated(payload["optimized"])
    return {
        "baseline_mitigated_tvd": float(baseline),
        "optimized_mitigated_tvd": float(optimized),
        "abs_difference": abs(float(optimized) - float(baseline)),
        "shots_per_job": int(payload.get("shots", 0)),
    }


def _hash(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build() -> dict:
    q0_payload = _load(Q0)
    q1_payload = _load(Q1)
    comparison = _load(COMPARISON)
    readout = _load(READOUT)
    q0 = _tomography_evidence(q0_payload)
    q1 = _tomography_evidence(q1_payload)
    readout_ev = _readout_evidence(readout)
    r1_delta = comparison["deltas"]["r1"]

    options = {}
    for half_width in HALF_WIDTHS:
        result = preregister_ci(
            p=P_PLANNING, half_width=half_width, confidence=CONFIDENCE
        )
        options[str(half_width)] = {
            "n_per_circuit": result["n"],
            "observed_half_width": result["observed_half_width"],
            "expected_interval": result["expected_interval"],
        }
    chosen = options["0.005"]

    coherence_ok = (
        q0["coherence_prep"] >= COHERENCE_GATE
        and q1["coherence_prep"] >= COHERENCE_GATE
    )
    r1_ok = q0["r1"] <= R1_GATE and q1["r1"] <= R1_GATE
    drift_unresolved = bool(
        r1_delta.get("ci_overlap")
        and abs(float(r1_delta["delta_q1_minus_q0"]))
        <= max(
            float(r1_delta["q0_set_spread"]),
            float(r1_delta["q1_set_spread"]),
        )
    )
    layout_effect_ok = readout_ev["abs_difference"] >= LAYOUT_EFFECT_GATE
    gates = {
        "coherence_prep_ge_0.99": {
            "pass": coherence_ok,
            "q0": q0["coherence_prep"],
            "q1": q1["coherence_prep"],
        },
        "r1_le_0.05": {
            "pass": r1_ok,
            "q0": q0["r1"],
            "q1": q1["r1"],
        },
        "layout_effect_ge_0.01": {
            "pass": layout_effect_ok,
            "observed": readout_ev["abs_difference"],
        },
        "drift_resolved": {
            "pass": not drift_unresolved,
            "delta_r1": r1_delta["delta_q1_minus_q0"],
            "q0_set_spread": r1_delta["q0_set_spread"],
            "q1_set_spread": r1_delta["q1_set_spread"],
        },
    }
    reasons = []
    if not coherence_ok:
        reasons.append("prep coerente abaixo de 0,99 em q0 e/ou q1")
    if not r1_ok:
        reasons.append("r1 acima de 0,05 em q0 e/ou q1")
    if not layout_effect_ok:
        reasons.append(
            "diferença de layout observada abaixo do efeito pré-registrado de 0,01"
        )
    if drift_unresolved:
        reasons.append("drift entre conjuntos não resolvido para r1")
    compare_now = all(item["pass"] for item in gates.values())

    budget = {
        "layouts": ["baseline", "optimized"],
        "circuits_per_layout": 3,
        "sets": 2,
        "jobs": 2 * 3 * 2,
        "shots_per_job": chosen["n_per_circuit"],
        "total_shots": 2 * 3 * 2 * chosen["n_per_circuit"],
        "note": (
            "3 circuitos = E05 + calibração 00 + calibração 11; "
            "2 conjuntos para estimar drift."
        ),
    }
    payload = {
        "schema_version": 1,
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "metric": "mitigated_tvd_vs_ideal",
        "planning": {
            "p": P_PLANNING,
            "confidence": CONFIDENCE,
            "effect_size": LAYOUT_EFFECT_GATE,
            "chosen_half_width": 0.005,
            "difference_half_width_approx": 2**0.5 * 0.005,
        },
        "n_options": options,
        "chosen": {
            "p": P_PLANNING,
            "confidence": CONFIDENCE,
            "half_width": 0.005,
            "n_per_circuit": chosen["n_per_circuit"],
        },
        "budget": budget,
        "gates": gates,
        "current_evidence": {
            "q0": q0,
            "q1": q1,
            "readout": readout_ev,
            "r1_delta": r1_delta,
        },
        "decision": {
            "compare_layouts_now": compare_now,
            "reasons": reasons if reasons else ["todos os gates passam"],
        },
        "stopping_rules": [
            "Não comparar layouts se qualquer gate falhar.",
            "Não interpretar sobreposição de IC como equivalência.",
            "Repetir 2 conjuntos e reportar drift antes de concluir.",
            "Não declarar vantagem de layout sem efeito ≥ 0,01 e IC excluindo 0.",
        ],
        "limits": (
            "Pré-registro local baseado em p=0,5 e meia-largura conservadora. "
            "TVD não é proporção; o cálculo é uma aproximação de planejamento."
        ),
        "hardware_executed": False,
    }
    payload["hash"] = _hash(payload)
    return payload


def report(payload: dict) -> str:
    gates = payload["gates"]
    lines = [
        "# Pré-registro de comparação de layouts",
        "",
        f"Gerado em {payload['created_at']}.",
        "",
        "## Decisão",
        "",
        f"- Comparar layouts agora: **{payload['decision']['compare_layouts_now']}**.",
        *[f"- {reason}." for reason in payload["decision"]["reasons"]],
        "",
        "## Gates",
        "",
        "| Gate | Passa? | Evidência |",
        "|---|---|---|",
        f"| prep coerente ≥ 0,99 | {gates['coherence_prep_ge_0.99']['pass']} | "
        f"q0={gates['coherence_prep_ge_0.99']['q0']:.4f}, "
        f"q1={gates['coherence_prep_ge_0.99']['q1']:.4f} |",
        f"| r1 ≤ 0,05 | {gates['r1_le_0.05']['pass']} | "
        f"q0={gates['r1_le_0.05']['q0']:.4f}, q1={gates['r1_le_0.05']['q1']:.4f} |",
        f"| efeito de layout ≥ 0,01 | {gates['layout_effect_ge_0.01']['pass']} | "
        f"diferença={gates['layout_effect_ge_0.01']['observed']:.4f} |",
        f"| drift resolvido | {gates['drift_resolved']['pass']} | "
        f"Δr1={gates['drift_resolved']['delta_r1']:+.4f} |",
        "",
        "## n pré-registrado",
        "",
        "| Meia-largura | n por circuito/layout |",
        "|---:|---:|",
    ]
    for half_width, item in payload["n_options"].items():
        lines.append(f"| {half_width} | {item['n_per_circuit']:,} |")
    lines += [
        "",
        f"Escolhido: n = **{payload['chosen']['n_per_circuit']:,}** por "
        f"circuito/layout (meia-largura 0,005; p=0,5; 95%).",
        "",
        "## Orçamento",
        "",
        f"- {payload['budget']['jobs']} jobs × "
        f"{payload['budget']['shots_per_job']:,} shots = "
        f"{payload['budget']['total_shots']:,} shots.",
        f"- {payload['budget']['note']}",
        "",
        "## Regras de parada",
        "",
        *[f"- {rule}" for rule in payload["stopping_rules"]],
        "",
        "## Limites",
        "",
        f"- {payload['limits']}",
        "",
        f"Hash SHA-256: `{payload['hash']}`.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    payload = build()
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    REPORT.write_text(report(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "ok",
                "preregistration": str(OUT),
                "report": str(REPORT),
                "compare_layouts_now": payload["decision"][
                    "compare_layouts_now"
                ],
                "n_per_circuit": payload["chosen"]["n_per_circuit"],
                "jobs": payload["budget"]["jobs"],
                "hash": payload["hash"],
                "hardware_executed": False,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
