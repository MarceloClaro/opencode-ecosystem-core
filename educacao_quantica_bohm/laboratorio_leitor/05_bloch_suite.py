#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Suíte de esfera de Bloch: vários circuitos, simulação e hardware.

Estados preparados:
- S1 |0⟩; S2 |1⟩; S3 |+⟩ (H); S4 |+i⟩ (H,S);
- S5 Ry(π/3)|0⟩; S6 H-RZ(π/2)-H|0⟩ (híbrido).

Para cada estado, mede Z, X e Y:
- Z: mede direto;
- X: H antes de medir;
- Y: S† e H antes de medir.

Componentes: ⟨Z⟩=P0−P1; ⟨X⟩ e ⟨Y⟩ idem após a rotação de base.
Salva counts, task IDs e vetores em dados_hardware/bloch_suite_guoji08.json.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

RAIZ = Path(__file__).resolve().parent
SAIDA = RAIZ / "dados"
SAIDA.mkdir(parents=True, exist_ok=True)

ESTADOS = [
    ("S1", "|0⟩", lambda q: None),
    ("S2", "|1⟩", lambda q: q.x(0)),
    ("S3", "|+⟩ = H|0⟩", lambda q: q.h(0)),
    ("S4", "|+i⟩ = S H|0⟩", lambda q: (q.h(0), q.s(0))),
    ("S5", "Ry(π/3)|0⟩", lambda q: q.ry(np.pi / 3, 0)),
    ("S6", "H-RZ(π/2)-H|0⟩", lambda q: (q.h(0), q.rz(np.pi / 2, 0), q.h(0))),
]

BASES = ["Z", "X", "Y"]


def preparar(nome: str) -> QuantumCircuit:
    qc = QuantumCircuit(1, 1)
    for codigo, _, fn in ESTADOS:
        if codigo == nome:
            fn(qc)
            return qc
    raise ValueError(nome)


def rotacao_base(qc: QuantumCircuit, base: str) -> None:
    if base == "X":
        qc.h(0)
    elif base == "Y":
        qc.sdg(0)
        qc.h(0)


def p0_sim(nome: str, base: str) -> float:
    qc = preparar(nome)
    rotacao_base(qc, base)
    return float(Statevector(qc).probabilities([0])[0])


def componente(p0: float) -> float:
    return 2 * p0 - 1


def simular() -> dict:
    dados = {}
    for codigo, rotulo, _ in ESTADOS:
        comp = {b: componente(p0_sim(codigo, b)) for b in BASES}
        dados[codigo] = {
            "rotulo": rotulo,
            "componentes": {"x": comp["X"], "y": comp["Y"], "z": comp["Z"]},
            "comprimento": float(np.linalg.norm([comp["X"], comp["Y"], comp["Z"]])),
        }
    return dados


def hardware(backend_nome: str, shots: int) -> dict:
    chave = os.environ.get("GJQ_API_KEY", "").strip()
    if not chave:
        raise SystemExit("GJQ_API_KEY ausente.")
    from gjq_client import GJQRuntimeService, Sampler, generate_preset_pass_manager

    servico = GJQRuntimeService(api_key=chave)
    backend = servico.backend(backend_nome)
    pm = generate_preset_pass_manager(backend=backend, optimization_level=2, seed_transpiler=42)
    dados = {}
    for codigo, rotulo, _ in ESTADOS:
        comp = {}
        counts = {}
        tids = {}
        for base in BASES:
            qc = preparar(codigo)
            rotacao_base(qc, base)
            qc.measure(0, 0)
            isa = pm.run(qc)
            job = Sampler(backend=backend).run(isa, shots=shots)
            c = {str(k): int(v) for k, v in job.result(timeout=900)["counts"].items()}
            counts[base] = c
            tids[base] = getattr(job, "_job_id", None)
            total = sum(c.values())
            comp[base] = componente(c.get("0", 0) / total)
            print(f"{codigo} {base}: {c} -> {comp[base]:+.3f}", flush=True)
        dados[codigo] = {
            "rotulo": rotulo,
            "componentes": {"x": comp["X"], "y": comp["Y"], "z": comp["Z"]},
            "comprimento": float(np.linalg.norm([comp["X"], comp["Y"], comp["Z"]])),
            "counts": counts,
            "task_ids": tids,
        }
    return dados


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="Guoji08")
    ap.add_argument("--shots", type=int, default=1024)
    ap.add_argument("--only", choices=["sim", "hardware", "all"], default="all")
    args = ap.parse_args()

    arquivo = SAIDA / "bloch_suite_guoji08.json"
    anterior = json.loads(arquivo.read_text(encoding="utf-8")) if arquivo.exists() else {}
    dados = {
        "backend": args.backend,
        "shots": args.shots,
        "estados": {c: r for c, r, _ in ESTADOS},
        "simulado": anterior.get("simulado", {}),
        "hardware": anterior.get("hardware", {}),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    if args.only in ("sim", "all"):
        dados["simulado"] = simular()
        print("Simulação concluída.")
    if args.only in ("hardware", "all"):
        dados["hardware"] = hardware(args.backend, args.shots)
        print("Hardware concluído.")

    arquivo.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
    print("JSON:", arquivo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
