#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Análise das repetições de leitura com mitigação (R1120/R1124).

Lê o run original e os dois conjuntos novos, compara TVD mitigada e verifica
se a diferença de layout é interpretável. Não executa hardware.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "gjq-hardware-optimizers" / "resultados" / "baihua"
RUNS = {
    "original": BASE / "E05_comparacao" / "comparacao.json",
    "set1": BASE / "E05_comparacao_set1" / "comparacao.json",
    "set2": BASE / "E05_comparacao_set2" / "comparacao.json",
}
OUT = (
    Path(__file__).resolve().parent
    / "resultados"
    / "readout_repeat.json"
)
REPORT = (
    Path(__file__).resolve().parent
    / "resultados"
    / "RELATORIO_READOUT_REPEAT.md"
)


def _mitigated(case: dict) -> float:
    value = case.get("mitigated_tvd_vs_ideal")
    if value is None:
        value = case.get("mitigated_tvd_subspace")
    if value is None:
        raise KeyError("caso sem TVD mitigada")
    return float(value)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build() -> dict:
    runs = {}
    for name, path in RUNS.items():
        if not path.exists():
            runs[name] = {"status": "missing", "path": str(path)}
            continue
        payload = _load(path)
        baseline = payload["baseline"]
        optimized = payload["optimized"]
        runs[name] = {
            "status": "ok",
            "shots": int(payload.get("shots", 0)),
            "baseline_mitigated_tvd": _mitigated(baseline),
            "optimized_mitigated_tvd": _mitigated(optimized),
            "delta_mitigated_tvd": (
                _mitigated(optimized) - _mitigated(baseline)
            ),
            "baseline_physical": baseline.get("candidate", {}).get("used_physical"),
            "optimized_physical": optimized.get("candidate", {}).get("used_physical"),
            "task_ids": {
                "baseline": baseline.get("task_id"),
                "optimized": optimized.get("task_id"),
            },
        }
    available = {name: item for name, item in runs.items() if item["status"] == "ok"}
    baseline_values = [item["baseline_mitigated_tvd"] for item in available.values()]
    optimized_values = [item["optimized_mitigated_tvd"] for item in available.values()]
    deltas = [item["delta_mitigated_tvd"] for item in available.values()]
    signs = {("optimized" if value < 0 else "baseline") for value in deltas}
    different_qubits = any(
        item["baseline_physical"] != item["optimized_physical"]
        for item in available.values()
    )
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "runs": runs,
        "summary": {
            "n_runs": len(available),
            "baseline_mean": sum(baseline_values) / len(baseline_values),
            "baseline_range": [min(baseline_values), max(baseline_values)],
            "optimized_mean": sum(optimized_values) / len(optimized_values),
            "optimized_range": [min(optimized_values), max(optimized_values)],
            "delta_mean": sum(deltas) / len(deltas),
            "delta_range": [min(deltas), max(deltas)],
            "sign_stable": len(signs) == 1,
            "different_physical_qubits": different_qubits,
        },
        "decision": {
            "compare_layouts_now": False,
            "reasons": [
                "o layout otimizado usa qubits físicos diferentes do baseline",
                "o sinal da diferença não é estável entre o run original e os dois novos",
                "os gates de prep coerente e r1 da R1120 continuam falhando",
                "a mitigação de leitura não reduz o r1 físico; mitigation ≠ correção do readout",
            ],
        },
        "limits": (
            "Três runs de 1 job por caso; não é série temporal. O layout "
            "otimizado usa 106/107 e o baseline usa 0/1, então a diferença "
            "mistura layout com qualidade de qubit."
        ),
        "hardware_executed": False,
    }
    return payload


def report(payload: dict) -> str:
    lines = [
        "# Repetição da leitura com mitigação",
        "",
        f"Gerado em {payload['generated_at']}.",
        "",
        "| Run | Baseline TVD | Otimizado TVD | Δ | Qubits baseline | Qubits otimizado |",
        "|---|---:|---:|---:|---|---|",
    ]
    for name, item in payload["runs"].items():
        if item["status"] != "ok":
            lines.append(f"| {name} | ausente | ausente | — | — | — |")
            continue
        lines.append(
            f"| {name} | {item['baseline_mitigated_tvd']:.4f} | "
            f"{item['optimized_mitigated_tvd']:.4f} | "
            f"{item['delta_mitigated_tvd']:+.4f} | "
            f"{item['baseline_physical']} | {item['optimized_physical']} |"
        )
    summary = payload["summary"]
    lines += [
        "",
        "## Resumo",
        "",
        f"- Runs disponíveis: {summary['n_runs']}.",
        f"- Baseline: média {summary['baseline_mean']:.4f}; "
        f"faixa {summary['baseline_range']}.",
        f"- Otimizado: média {summary['optimized_mean']:.4f}; "
        f"faixa {summary['optimized_range']}.",
        f"- Δ: média {summary['delta_mean']:+.4f}; faixa {summary['delta_range']}.",
        f"- Sinal estável entre runs: {summary['sign_stable']}.",
        f"- Qubits físicos diferentes: {summary['different_physical_qubits']}.",
        "",
        "## Decisão",
        "",
        f"- Comparar layouts agora: **{payload['decision']['compare_layouts_now']}**.",
        *[f"- {reason}." for reason in payload["decision"]["reasons"]],
        "",
        "## Limites",
        "",
        f"- {payload['limits']}",
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
                "analysis": str(OUT),
                "report": str(REPORT),
                "summary": payload["summary"],
                "compare_layouts_now": payload["decision"]["compare_layouts_now"],
                "hardware_executed": False,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
