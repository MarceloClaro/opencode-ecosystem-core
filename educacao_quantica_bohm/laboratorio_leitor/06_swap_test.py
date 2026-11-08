#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prática Tiangong: SWAP test para estimar a sobreposição de dois estados.

Circuito do guia da Tiangong:
- q0: ancilla;
- q1: |psi> = |0>;
- q2: |phi> = Ry(1.0)|0>;
- H, CSWAP, H, medir q0.

Ideal: P(0) = (1 + |<psi|phi>|^2)/2 = 0,8851; overlap = 0,7702.
O script simula, envia ao Guoji08 e salva counts/task ID em dados_hardware/.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
from qiskit import QuantumCircuit, qasm2
from qiskit.quantum_info import Statevector

RAIZ = Path(__file__).resolve().parent
SAIDA = RAIZ / "dados"
SAIDA.mkdir(parents=True, exist_ok=True)

QASM = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg c[1];
ry(1.000000) q[2];
h q[0];
cswap q[0],q[1],q[2];
h q[0];
measure q[0] -> c[0];
"""


def circuito() -> QuantumCircuit:
    # Qiskit 2.x não resolve `cswap` no parser QASM2; montamos com a porta nativa.
    qc = QuantumCircuit(3, 1)
    qc.ry(1.0, 2)
    qc.h(0)
    qc.cswap(0, 1, 2)
    qc.h(0)
    qc.measure(0, 0)
    return qc


def simular() -> float:
    qc = circuito().remove_final_measurements(inplace=False)
    probs = Statevector(qc).probabilities([0])
    return float(probs[0])


def main() -> int:
    p0_sim = simular()
    overlap_sim = 2 * p0_sim - 1
    print(f"P(0) simulado: {p0_sim:.4f}; overlap: {overlap_sim:.4f}")

    chave = os.environ.get("GJQ_API_KEY", "").strip()
    if not chave:
        print("GJQ_API_KEY ausente; salvando apenas a simulação.", file=sys.stderr)
        dados = {
            "qasm": QASM,
            "p0_sim": p0_sim,
            "overlap_sim": overlap_sim,
            "real": None,
            "timestamp": datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
        }
    else:
        from gjq_client import GJQRuntimeService, Sampler, generate_preset_pass_manager

        servico = GJQRuntimeService(api_key=chave)
        backend = servico.backend("Guoji08")
        pm = generate_preset_pass_manager(backend=backend, optimization_level=2, seed_transpiler=42)
        isa = pm.run(circuito())
        job = Sampler(backend=backend).run(isa, shots=1024)
        counts = {str(k): int(v) for k, v in job.result(timeout=900)["counts"].items()}
        n0 = counts.get("0", 0)
        n1 = counts.get("1", 0)
        total = n0 + n1
        p0_hw = n0 / total
        overlap_hw = 2 * p0_hw - 1
        dados = {
            "qasm": QASM,
            "p0_sim": p0_sim,
            "overlap_sim": overlap_sim,
            "real": {
                "backend": backend.name,
                "shots": 1024,
                "counts": counts,
                "p0": p0_hw,
                "overlap": overlap_hw,
                "task_id": getattr(job, "_job_id", None),
            },
            "timestamp": datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
        }
        print(f"P(0) backend: {p0_hw:.4f}; overlap: {overlap_hw:.4f}; counts={counts}")

    saida = SAIDA / "swap_test_guoji08.json"
    saida.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
    print("JSON:", saida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
