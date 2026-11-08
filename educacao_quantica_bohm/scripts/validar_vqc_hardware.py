#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Avalia um VQC de 4 qubits treinado no simulador em hardware (Guoji08).

Treina o modelo com 50 amostras (seed 0), escolhe 4 pontos de teste e envia
cada circuito ao backend com 1024 tiros. Compara P(1) simulado e observado.
A API key é lida apenas de GJQ_API_KEY; nunca é gravada.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))

from validar_vqc_forte import circuito, p1, treinar, two_moons  # noqa: E402


def main() -> int:
    chave = os.environ.get("GJQ_API_KEY", "").strip()
    if not chave:
        print("GJQ_API_KEY ausente.", file=sys.stderr)
        return 2

    X, y = two_moons()
    rng = np.random.default_rng(0)
    idx = rng.permutation(len(y))
    tr, te = idx[:50], idx[50:]
    theta = treinar(X, y, tr, 4, seed=0)

    # 4 pontos: dois de cada classe
    escolhidos = []
    for classe in (0, 1):
        for i in te:
            if y[i] == classe and len(escolhidos) < 4:
                escolhidos.append(int(i))
            if len([j for j in escolhidos if y[j] == classe]) >= 2:
                break

    from qiskit import QuantumCircuit
    from gjq_client import GJQRuntimeService, Sampler, generate_preset_pass_manager

    servico = GJQRuntimeService(api_key=chave)
    backend = servico.backend("Guoji08")
    pm = generate_preset_pass_manager(backend=backend, optimization_level=2, seed_transpiler=42)

    resultados = []
    for i in escolhidos:
        qc = circuito(X[i], theta, 4)
        qc.measure(0, 0)
        isa = pm.run(qc)
        job = Sampler(backend=backend).run(isa, shots=1024)
        counts = {str(k): int(v) for k, v in job.result(timeout=900)["counts"].items()}
        total = sum(counts.values())
        p_hw = counts.get("1", 0) / total
        p_sim = p1(X[i], theta, 4)
        resultados.append({
            "indice": i,
            "x": X[i].tolist(),
            "y": int(y[i]),
            "p1_sim": p_sim,
            "p1_hw": p_hw,
            "pred_sim": int(p_sim >= 0.5),
            "pred_hw": int(p_hw >= 0.5),
            "counts": counts,
            "task_id": getattr(job, "_job_id", None),
        })
        print(f"ponto {i}: y={y[i]} sim={p_sim:.3f} hw={p_hw:.3f}", flush=True)

    acertos = sum(1 for r in resultados if r["pred_hw"] == r["y"])
    dados = {
        "backend": backend.name,
        "n_qubits": 4,
        "shots": 1024,
        "seed": 0,
        "resultados": resultados,
        "acuracia_hw": acertos / len(resultados),
        "timestamp": __import__("datetime").datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    saida = RAIZ / "dados_qualis" / "vqc_4q_hardware.json"
    saida.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
    print("JSON:", saida)
    print(f"Acurácia hardware: {acertos}/{len(resultados)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())