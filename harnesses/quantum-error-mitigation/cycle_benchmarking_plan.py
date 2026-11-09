#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Plano de cycle benchmarking para as 15 taxas Pauli-Lindblad (R1122).

Gera apenas o plano de jobs e o orçamento. Não executa hardware e não mede
taxas.
"""
from __future__ import annotations

import itertools
import json
from datetime import datetime
from pathlib import Path

OUT = Path(__file__).resolve().parent / "resultados" / "cycle_benchmarking_plan.json"
REPORT = (
    Path(__file__).resolve().parent
    / "resultados"
    / "RELATORIO_CYCLE_BENCHMARKING_PLAN.md"
)
DEPTHS = (1, 2, 4, 8, 16)
SETS = 2
SHOTS = 4096
PROCESS_LIMIT = 20
PAULIS_2Q = [
    "".join(chars)
    for chars in itertools.product("IXYZ", repeat=2)
    if chars != ("I", "I")
]


def build() -> dict:
    jobs = len(PAULIS_2Q) * len(DEPTHS) * SETS
    processes = (jobs + PROCESS_LIMIT - 1) // PROCESS_LIMIT
    return {
        "schema_version": 1,
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "gate": "cz",
        "qubits": [0, 1],
        "paulis": PAULIS_2Q,
        "depths": list(DEPTHS),
        "sets": SETS,
        "shots": SHOTS,
        "jobs": jobs,
        "processes": processes,
        "process_limit": PROCESS_LIMIT,
        "total_shots": jobs * SHOTS,
        "analysis": (
            "Ajuste exponencial da sobrevivência por Pauli; converter "
            "fidelidades em taxas Pauli-Lindblad; reportar IC."
        ),
        "prerequisites": [
            "passe de Pauli-frame R1119",
            "mitigação de leitura",
            "n por profundidade pré-registrado",
            "GST ou Rabi para separar SPAM",
        ],
        "rates_measured": False,
        "hardware_executed": False,
        "limits": (
            "Plano de jobs; nenhuma taxa foi medida. 150 jobs é piso de "
            "planejamento, não garantia de poder estatístico."
        ),
    }


def report(payload: dict) -> str:
    return "\n".join(
        [
            "# Plano de cycle benchmarking — 15 taxas Pauli-Lindblad",
            "",
            f"Gerado em {payload['created_at']}.",
            "",
            "## Plano",
            "",
            f"- Porta: `{payload['gate']}` em {payload['qubits']}.",
            f"- Paulis: {len(payload['paulis'])}.",
            f"- Profundidades: {payload['depths']}.",
            f"- Conjuntos: {payload['sets']}.",
            f"- Jobs: **{payload['jobs']}**.",
            f"- Processos (limite {payload['process_limit']}): {payload['processes']}.",
            f"- Shots por job: {payload['shots']:,}.",
            f"- Shots totais: {payload['total_shots']:,}.",
            "",
            "## Análise",
            "",
            f"- {payload['analysis']}",
            "",
            "## Pré-requisitos",
            "",
            *[f"- {item}" for item in payload["prerequisites"]],
            "",
            "## Limites",
            "",
            "- Nenhuma taxa foi medida.",
            "- O plano não executa hardware.",
            f"- {payload['limits']}",
            "",
        ]
    )


def main() -> int:
    payload = build()
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    REPORT.write_text(report(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "ok",
                "plan": str(OUT),
                "report": str(REPORT),
                "paulis": len(payload["paulis"]),
                "jobs": payload["jobs"],
                "processes": payload["processes"],
                "rates_measured": False,
                "hardware_executed": False,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
