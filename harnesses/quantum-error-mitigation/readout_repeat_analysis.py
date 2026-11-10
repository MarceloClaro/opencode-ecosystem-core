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


def _metric_scope(case: dict) -> str:
    states = set(case.get("calibration_counts", {}))
    if states == {"00", "11"}:
        return "subspace_00_11"
    if states == {"00", "01", "10", "11"}:
        return "full_4x4"
    return "unknown"


def _mitigated(case: dict) -> float:
    # Campo vs_ideal também existia nos runs com calibração parcial.
    # O nome do campo não transforma calibração 00/11 em matriz 4x4.
    value = (case.get("mitigated_tvd_subspace") if _metric_scope(case) == "subspace_00_11"
             else case.get("mitigated_tvd_vs_ideal"))
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
            "baseline_metric_scope": _metric_scope(baseline),
            "optimized_metric_scope": _metric_scope(optimized),
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
    def mean(values):
        return sum(values)/len(values) if values else None

    def span(values):
        return [min(values), max(values)] if values else None

    reasons = [
        "os gates de prep coerente e r1 da R1120 não foram reavaliados isoladamente aqui",
        "a mitigação de leitura não reduz o r1 bruto, que inclui erro de preparação",
    ]
    if not available:
        reasons.append("dados ausentes: nenhuma comparação possível")
    elif len(signs) > 1:
        reasons.append("o sinal da diferença não é estável entre runs")
    if different_qubits:
        reasons.append("qubits físicos diferentes: efeito total de mapeamento não isola a transpilação")
    if any(item[f"{arm}_metric_scope"] != "full_4x4"
           for item in available.values() for arm in ("baseline", "optimized")):
        reasons.append("calibração de subespaço 00/11 ou desconhecida, não uma matriz 4x4 completa")
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "runs": runs,
        "summary": {
            "n_runs": len(available),
            "baseline_mean": mean(baseline_values),
            "baseline_range": span(baseline_values),
            "optimized_mean": mean(optimized_values),
            "optimized_range": span(optimized_values),
            "delta_mean": mean(deltas),
            "delta_range": span(deltas),
            "sign_stable": bool(deltas) and len(signs) == 1,
            "different_physical_qubits": different_qubits,
        },
        "decision": {
            "compare_layouts_now": False,
            "r1_gate_remeasured": False,
            "reasons": reasons,
        },
        "limits": (
            "Runs históricos de 1 job por caso; não é série temporal nem ensaio "
            "com n da R1120. Calibração somente 00/11 mede subespaço, não TVD "
            "completa corrigida. Qubits diferentes são parte do efeito de "
            "mapeamento; não invalidam por si uma comparação pré-registrada."
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
        "TVD do **subespaço 00/11** nos três runs históricos, não calibração 4×4.",
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
    def fmt(value):
        return "indisponível" if value is None else f"{value:.4f}"
    lines += [
        "",
        "## Resumo",
        "",
        f"- Runs disponíveis: {summary['n_runs']}.",
        f"- Baseline: média {fmt(summary['baseline_mean'])}; "
        f"faixa {summary['baseline_range']}.",
        f"- Otimizado: média {fmt(summary['optimized_mean'])}; "
        f"faixa {summary['optimized_range']}.",
        f"- Δ: média {fmt(summary['delta_mean'])}; faixa {summary['delta_range']}.",
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
