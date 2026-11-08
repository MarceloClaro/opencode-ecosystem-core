#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Executa experimentos no backend da nuvem quântica pelo `gjq-client`.

Experimentos
------------
- ``ghz``  : GHZ de 4 qubits (H + três CNOTs), 1024 tiros.
- ``qasm`` : o mesmo GHZ, mas carregado de um texto OpenQASM 2.0.
- ``vqc``  : classificador XOR de 2 qubits com ângulos fixos.
- ``chsh`` : quatro configurações de CHSH e o valor S.

A API key é lida **somente** de ``GJQ_API_KEY``. O script nunca grava a chave
em arquivo, log ou JSON. Os resultados vão para ``dados_hardware/`` com os
task IDs de cada submissão.

Uso
---
    export GJQ_API_KEY="..."
    python educacao_quantica_bohm/scripts/executar_nuvem.py --backend Guoji08
    python educacao_quantica_bohm/scripts/executar_nuvem.py --only ghz chsh
    python educacao_quantica_bohm/scripts/executar_nuvem.py --dry-run

O modo ``--dry-run`` monta e transpila os circuitos localmente, sem rede e sem
chave. Ele serve para testar o script antes de gastar fila de hardware.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, qasm2

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "dados_hardware"
QASM_GHZ = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[4];
creg c[4];
h q[0];
cx q[0], q[1];
cx q[0], q[2];
cx q[0], q[3];
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
"""

THETA_PADRAO = [1.5708, 1.5708, -1.5708, 2.819]
XOR = [(0, 0), (0, 1), (1, 0), (1, 1)]
CHSH = [
    ("E00", 0, -np.pi / 4),
    ("E01", 0, np.pi / 4),
    ("E10", 1, -np.pi / 4),
    ("E11", 1, np.pi / 4),
]
EXPERIMENTOS = ("ghz", "qasm", "vqc", "chsh")


def agora() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def slug_backend(nome: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in nome).strip("_").lower()


def circuito_ghz() -> QuantumCircuit:
    qc = QuantumCircuit(4, 4)
    qc.h(0)
    for alvo in (1, 2, 3):
        qc.cx(0, alvo)
    qc.measure([0, 1, 2, 3], [0, 1, 2, 3])
    return qc


def circuito_vqc(x: tuple[int, int], theta: list[float]) -> QuantumCircuit:
    qc = QuantumCircuit(2, 1)
    qc.ry(np.pi * x[0], 0)
    qc.ry(np.pi * x[1], 1)
    qc.ry(theta[0], 0)
    qc.ry(theta[1], 1)
    qc.cx(0, 1)
    qc.ry(theta[2], 0)
    qc.ry(theta[3], 1)
    qc.measure(0, 0)
    return qc


def circuito_chsh(a1: int, angulo: float) -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    if a1:
        qc.h(0)
    qc.ry(angulo, 1)
    qc.measure([0, 1], [0, 1])
    return qc


def contagens_limpas(counts: Any) -> dict[str, int]:
    return {str(k): int(v) for k, v in dict(counts).items()}


def task_id(job: Any) -> Any:
    tid = getattr(job, "_job_id", None)
    if isinstance(tid, (list, tuple)) and len(tid) == 1:
        tid = tid[0]
    if isinstance(tid, (str, int)) or tid is None:
        return tid
    return str(tid)


def chave_api() -> str:
    chave = os.environ.get("GJQ_API_KEY", "").strip()
    if not chave:
        raise SystemExit(
            "GJQ_API_KEY ausente.\n"
            "Defina a chave apenas no ambiente, por exemplo:\n"
            '  export GJQ_API_KEY="sua-chave"\n'
            "Nunca grave a chave em arquivo do projeto."
        )
    return chave


def carregar(backend_nome: str, timeout: float):
    from gjq_client import GJQRuntimeService

    servico = GJQRuntimeService(api_key=chave_api())
    backend = servico.backend(backend_nome)
    return servico, backend


def transpilar(qc: QuantumCircuit, backend, seed: int, nivel: int):
    """Transpila para o backend real ou para um backend local de teste.

    O `generate_preset_pass_manager` do gjq-client espera a interface V1
    (`backend.configuration()`); o backend falso usado no `--dry-run` é V2.
    Nesse caso, usamos o transpilador do próprio Qiskit.
    """
    try:
        backend.configuration()
    except Exception:
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    else:
        from gjq_client import generate_preset_pass_manager

    pm = generate_preset_pass_manager(
        backend=backend, optimization_level=nivel, seed_transpiler=seed
    )
    return pm.run(qc)


def executar(backend, qc: QuantumCircuit, shots: int, timeout: float) -> tuple[dict[str, int], Any]:
    from gjq_client import Sampler

    job = Sampler(backend=backend).run(qc, shots=shots)
    tid = task_id(job)
    counts = job.result(timeout=timeout)["counts"]
    return contagens_limpas(counts), tid


def exp_ghz(backend, shots: int, timeout: float, seed: int, nivel: int) -> dict:
    bruto = circuito_ghz()
    isa = transpilar(bruto, backend, seed, nivel)
    counts, tid = executar(backend, isa, shots, timeout)
    total = sum(counts.values())
    ideal = counts.get("0000", 0) + counts.get("1111", 0)
    return {
        "experimento": "ghz",
        "backend": backend.name,
        "n_qubits": 4,
        "shots": shots,
        "depth_original": bruto.depth(),
        "depth_transpilado": isa.depth(),
        "counts": counts,
        "fidelidade_proxy": ideal / total if total else None,
        "task_ids": [tid],
        "timestamp": agora(),
    }


def exp_qasm(backend, shots: int, timeout: float, seed: int, nivel: int) -> dict:
    bruto = qasm2.loads(QASM_GHZ)
    isa = transpilar(bruto, backend, seed, nivel)
    counts, tid = executar(backend, isa, shots, timeout)
    total = sum(counts.values())
    ideal = counts.get("0000", 0) + counts.get("1111", 0)
    return {
        "experimento": "qasm",
        "backend": backend.name,
        "n_qubits": 4,
        "shots": shots,
        "qasm": QASM_GHZ,
        "depth_original": bruto.depth(),
        "depth_transpilado": isa.depth(),
        "counts": counts,
        "fidelidade_proxy": ideal / total if total else None,
        "task_ids": [tid],
        "timestamp": agora(),
    }


def exp_vqc(backend, shots: int, timeout: float, seed: int, nivel: int,
            theta: list[float]) -> dict:
    resultados = []
    tids = []
    for x in XOR:
        bruto = circuito_vqc(x, theta)
        isa = transpilar(bruto, backend, seed, nivel)
        counts, tid = executar(backend, isa, shots, timeout)
        tids.append(tid)
        total = sum(counts.values())
        p1 = counts.get("1", 0) / total if total else 0.0
        y = 1 if x[0] != x[1] else 0
        pred = 1 if p1 >= 0.5 else 0
        resultados.append({
            "x": list(x),
            "y": y,
            "counts": counts,
            "p1": p1,
            "pred": pred,
        })
    acertos = sum(1 for r in resultados if r["pred"] == r["y"])
    return {
        "experimento": "vqc",
        "backend": backend.name,
        "n_qubits": 2,
        "shots": shots,
        "theta": theta,
        "resultados": resultados,
        "acuracia": acertos / len(resultados),
        "task_ids": tids,
        "timestamp": agora(),
    }


def exp_chsh(backend, shots: int, timeout: float, seed: int, nivel: int) -> dict:
    counts: dict[str, dict[str, int]] = {}
    tids = []
    for nome, a1, angulo in CHSH:
        bruto = circuito_chsh(a1, float(angulo))
        isa = transpilar(bruto, backend, seed, nivel)
        c, tid = executar(backend, isa, shots, timeout)
        counts[nome] = c
        tids.append(tid)

    E = {}
    for nome, c in counts.items():
        total = sum(c.values())
        n00, n01, n10, n11 = (c.get(k, 0) for k in ("00", "01", "10", "11"))
        E[nome] = (n00 + n11 - n01 - n10) / total if total else 0.0
    S = E["E00"] + E["E01"] + E["E10"] - E["E11"]
    return {
        "experimento": "chsh",
        "backend": backend.name,
        "n_qubits": 2,
        "shots": shots,
        "counts": counts,
        "E": E,
        "S": S,
        "ideal_S": 2 * np.sqrt(2),
        "task_ids": tids,
        "timestamp": agora(),
    }


def escrever(caminho: Path, dados: dict) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")


def salvar_por_experimento(resultados: dict[str, dict], backend: str, saida: Path) -> list[Path]:
    sufixo = slug_backend(backend)
    arquivos = []
    mapa = {
        "ghz": f"ghz4_{sufixo}.json",
        "qasm": f"ghz4_qasm_{sufixo}.json",
        "vqc": f"vqc_xor_{sufixo}.json",
        "chsh": f"chsh_{sufixo}.json",
    }
    for nome, dados in resultados.items():
        if "erro" in dados:
            continue
        caminho = saida / mapa[nome]
        escrever(caminho, dados)
        arquivos.append(caminho)
    return arquivos


def dry_run(backend_nome: str, theta: list[float], seed: int, nivel: int) -> int:
    from qiskit.providers.fake_provider import GenericBackendV2

    backend = GenericBackendV2(num_qubits=5, seed=seed)
    circuitos = {
        "ghz": [circuito_ghz()],
        "qasm": [qasm2.loads(QASM_GHZ)],
        "vqc": [circuito_vqc(x, theta) for x in XOR],
        "chsh": [circuito_chsh(a1, float(angulo)) for _, a1, angulo in CHSH],
    }
    print(f"[dry-run] backend simulado: {backend.name} ({backend.num_qubits} qubits)")
    for nome, lista in circuitos.items():
        for i, qc in enumerate(lista, 1):
            isa = transpilar(qc, backend, seed, nivel)
            print(
                f"  {nome}[{i}] qubits={qc.num_qubits} "
                f"depth={qc.depth()} -> {isa.depth()} "
                f"ops={dict(qc.count_ops())}"
            )
    print("[dry-run] circuitos válidos; nenhuma submissão foi feita.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--backend", default="Guoji08", help="backend da plataforma (padrão: Guoji08)")
    ap.add_argument("--shots", type=int, default=1024, help="tiros por circuito")
    ap.add_argument("--timeout", type=float, default=900.0, help="espera por job, em segundos")
    ap.add_argument("--seed-transpiler", type=int, default=42)
    ap.add_argument("--optimization-level", type=int, default=2, choices=[0, 1, 2, 3])
    ap.add_argument("--only", nargs="+", choices=EXPERIMENTOS, default=list(EXPERIMENTOS))
    ap.add_argument("--output-dir", type=Path, default=DADOS)
    ap.add_argument("--theta", nargs=4, type=float, default=None,
                    help="ângulos do VQC (padrão: lê o JSON existente ou usa 1.5708 1.5708 -1.5708 2.819)")
    ap.add_argument("--dry-run", action="store_true", help="monta circuitos sem rede/chave")
    args = ap.parse_args()

    theta = args.theta
    if theta is None:
        anterior = DADOS / "vqc_xor_guoji08.json"
        if anterior.exists():
            try:
                theta = json.loads(anterior.read_text(encoding="utf-8"))["theta"]
            except Exception:
                theta = THETA_PADRAO
        else:
            theta = THETA_PADRAO

    if args.dry_run:
        return dry_run(args.backend, theta, args.seed_transpiler, args.optimization_level)

    if args.shots <= 0:
        raise SystemExit("--shots deve ser positivo")
    if args.timeout <= 0:
        raise SystemExit("--timeout deve ser positivo")

    servico, backend = carregar(args.backend, args.timeout)
    print(f"Backend: {backend.name} | shots={args.shots} | experimentos={args.only}")

    executores = {
        "ghz": lambda: exp_ghz(backend, args.shots, args.timeout, args.seed_transpiler,
                               args.optimization_level),
        "qasm": lambda: exp_qasm(backend, args.shots, args.timeout, args.seed_transpiler,
                                 args.optimization_level),
        "vqc": lambda: exp_vqc(backend, args.shots, args.timeout, args.seed_transpiler,
                               args.optimization_level, theta),
        "chsh": lambda: exp_chsh(backend, args.shots, args.timeout, args.seed_transpiler,
                                 args.optimization_level),
    }

    resultados: dict[str, dict] = {}
    falhas = 0
    for nome in args.only:
        print(f"\n== {nome} ==")
        inicio = time.monotonic()
        try:
            dados = executores[nome]()
            resultados[nome] = dados
            print(f"   ok em {time.monotonic() - inicio:.1f}s | task_ids={dados.get('task_ids')}")
        except Exception as exc:  # uma falha não deve apagar os outros resultados
            falhas += 1
            resultados[nome] = {"experimento": nome, "erro": f"{type(exc).__name__}: {exc}"}
            print(f"   FALHOU: {type(exc).__name__}: {exc}", file=sys.stderr)

    consolidado = {
        "backend": backend.name,
        "shots": args.shots,
        "experimentos": args.only,
        "resultados": resultados,
        "falhas": falhas,
        "timestamp": agora(),
    }
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    combinado = args.output_dir / f"nuvem_{slug_backend(backend.name)}_{carimbo}.json"
    escrever(combinado, consolidado)
    arquivos = salvar_por_experimento(resultados, backend.name, args.output_dir)

    print("\n== resumo ==")
    for nome, dados in resultados.items():
        if "erro" in dados:
            print(f"{nome}: ERRO — {dados['erro']}")
        elif nome == "ghz":
            print(f"ghz: fidelidade proxy {dados['fidelidade_proxy']:.1%}")
        elif nome == "qasm":
            print(f"qasm: fidelidade proxy {dados['fidelidade_proxy']:.1%}")
        elif nome == "vqc":
            print(f"vqc: acurácia {dados['acuracia']:.0%} ({len(dados['resultados'])} pontos)")
        elif nome == "chsh":
            print(f"chsh: S = {dados['S']:.4f} (ideal {dados['ideal_S']:.4f})")

    print(f"\nconsolidado: {combinado}")
    for caminho in arquivos:
        print(f"arquivo: {caminho}")
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())