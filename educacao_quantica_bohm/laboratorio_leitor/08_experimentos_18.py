#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Versão standalone dos 18 experimentos-base do livro.

Roda a simulação local (statevector + amostragem), envia ao backend
Tiangong/Guoji quando solicitado e grava JSON + CSV em `dados/`.

Uso:
    python 08_experimentos_18.py --sim
    python 08_experimentos_18.py --sim --only E09
    python 08_experimentos_18.py --real --backend Guoji08 --only E09
    python 08_experimentos_18.py --report

A chave é lida somente de GJQ_API_KEY. O script nunca grava a chave.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFTGate
from qiskit.quantum_info import Statevector

RAIZ = Path(__file__).resolve().parent
SAIDA = RAIZ / "dados"
SAIDA.mkdir(parents=True, exist_ok=True)

XOR = [(0, 0), (0, 1), (1, 0), (1, 1)]
THETA = [1.5708, 1.5708, -1.5708, 2.819]
CHSH = [("E00", 0, -np.pi / 4), ("E01", 0, np.pi / 4),
        ("E10", 1, -np.pi / 4), ("E11", 1, np.pi / 4)]


def agora() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def _p(counts: dict, chave: str) -> float:
    total = sum(int(v) for v in counts.values())
    return int(counts.get(chave, 0)) / total if total else 0.0


def _soma(counts: dict, chaves: tuple[str, ...]) -> float:
    return sum(_p(counts, c) for c in chaves)


# ---------------------------------------------------------------- circuitos

def qc_basis0() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1); qc.measure(0, 0); return qc


def qc_basis1() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1); qc.x(0); qc.measure(0, 0); return qc


def qc_superposicao() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1); qc.h(0); qc.measure(0, 0); return qc


def qc_fase() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1); qc.h(0); qc.z(0); qc.h(0); qc.measure(0, 0); return qc


def qc_bell() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2); qc.h(0); qc.cx(0, 1)
    qc.measure([0, 1], [0, 1]); return qc


def qc_ghz4() -> QuantumCircuit:
    qc = QuantumCircuit(4, 4); qc.h(0)
    for alvo in (1, 2, 3):
        qc.cx(0, alvo)
    qc.measure([0, 1, 2, 3], [0, 1, 2, 3]); return qc


def qc_chsh(a1: int, angulo: float) -> QuantumCircuit:
    qc = QuantumCircuit(2, 2); qc.h(0); qc.cx(0, 1)
    if a1:
        qc.h(0)
    qc.ry(angulo, 1); qc.measure([0, 1], [0, 1]); return qc


def qcs_chsh() -> list[QuantumCircuit]:
    return [qc_chsh(a1, float(ang)) for _, a1, ang in CHSH]


def qc_qrng() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1); qc.h(0); qc.measure(0, 0); return qc


def qc_amplitude() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1); qc.ry(2 * np.pi / 3, 0); qc.measure(0, 0); return qc


def qc_vqc(x: tuple[int, int]) -> QuantumCircuit:
    qc = QuantumCircuit(2, 1)
    qc.ry(np.pi * x[0], 0); qc.ry(np.pi * x[1], 1)
    qc.ry(THETA[0], 0); qc.ry(THETA[1], 1)
    qc.cx(0, 1)
    qc.ry(THETA[2], 0); qc.ry(THETA[3], 1)
    qc.measure(0, 0); return qc


def qcs_vqc() -> list[QuantumCircuit]:
    return [qc_vqc(x) for x in XOR]


def qc_interferencia2() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2); qc.h(0); qc.h(1); qc.cz(0, 1); qc.h(0)
    qc.measure([0, 1], [0, 1]); return qc


def qc_qft3() -> QuantumCircuit:
    qc = QuantumCircuit(3, 3); qc.x(2); qc.append(QFTGate(3), range(3))
    qc.measure([0, 1, 2], [0, 1, 2]); return qc


def qc_tensor01() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2); qc.x(0); qc.measure([0, 1], [0, 1]); return qc


def qc_ruido_phase() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1); qc.h(0); qc.x(0); qc.h(0); qc.measure(0, 0); return qc


def qc_walk3() -> QuantumCircuit:
    qc = QuantumCircuit(3, 3); qc.h(0); qc.h(1); qc.h(2)
    qc.cz(0, 1); qc.cz(1, 2); qc.h(0); qc.h(1); qc.h(2)
    qc.measure([0, 1, 2], [0, 1, 2]); return qc


# ---------------------------------------------------------------- leituras

def leitura_p0(cs): return f"P(0) = {_p(cs[0], '0'):.3f} (ideal 1,000)"
def leitura_p1(cs): return f"P(1) = {_p(cs[0], '1'):.3f} (ideal 1,000)"
def leitura_superposicao(cs): return f"P(1) = {_p(cs[0], '1'):.3f} (ideal 0,500)"
def leitura_fase(cs): return f"P(1) = {_p(cs[0], '1'):.3f} (ideal 1,000)"
def leitura_bell(cs): return f"P(00)+P(11) = {_soma(cs[0], ('00', '11')):.3f} (ideal 1,000)"
def leitura_ghz(cs): return f"P(0000)+P(1111) = {_soma(cs[0], ('0000', '1111')):.3f} (ideal 1,000)"


def leitura_chsh(cs):
    E = [_p(c, "00") + _p(c, "11") - _p(c, "01") - _p(c, "10") for c in cs]
    return f"S = {E[0] + E[1] + E[2] - E[3]:.3f} (ideal 2,828)"


def leitura_qrng(cs):
    return f"|P(0)-P(1)| = {abs(_p(cs[0], '0') - _p(cs[0], '1')):.3f} (ideal 0,000)"


def leitura_amplitude(cs): return f"P(1) = {_p(cs[0], '1'):.3f} (ideal 0,750)"


def leitura_vqc(cs):
    acertos = 0
    for c, x in zip(cs, XOR):
        y = 1 if x[0] != x[1] else 0
        pred = 1 if _p(c, "1") >= 0.5 else 0
        acertos += int(pred == y)
    return f"Acurácia = {acertos}/4"


def leitura_interferencia2(cs): return f"P(00) = {_p(cs[0], '00'):.3f} (ideal 0,500)"
def leitura_qft3(cs): return f"P(000) = {_p(cs[0], '000'):.3f} (ideal 0,125)"
def leitura_tensor01(cs): return f"P(01) = {_p(cs[0], '01'):.3f} (ideal 1,000)"
def leitura_ruido(cs): return f"P(0) = {_p(cs[0], '0'):.3f} (ideal 1,000)"


def leitura_bloch(cs):
    return f"⟨Z⟩ = {2*_p(cs[0], '0')-1:+.3f}, ⟨X⟩ = {2*_p(cs[1], '0')-1:+.3f} (ideal 0, +1)"


def leitura_walk3(cs): return f"P(000) = {_p(cs[0], '000'):.3f} (ideal 0,250)"
def leitura_amostragem(cs): return f"P(1) = {_p(cs[0], '1'):.3f} (ideal 0,500)"


EXPERIMENTOS = {
    "E01": ("Base |0⟩", "Prepara |0⟩ e mede 1024 vezes.", lambda: [qc_basis0()], leitura_p0),
    "E02": ("Base |1⟩ e leitura", "Prepara |1⟩ e mede; a discrepância é erro de leitura.", lambda: [qc_basis1()], leitura_p1),
    "E03": ("Superposição H|0⟩", "H cria uma superposição; a medição produz 0 ou 1.", lambda: [qc_superposicao()], leitura_superposicao),
    "E04": ("Interferência H-Z-H", "A fase Z inverte a interferência: o resultado vira |1⟩.", lambda: [qc_fase()], leitura_fase),
    "E05": ("Estado de Bell", "H + CNOT criam uma correlação 00/11.", lambda: [qc_bell()], leitura_bell),
    "E06": ("GHZ de 4 qubits", "Quatro qubits compartilham 0000/1111.", lambda: [qc_ghz4()], leitura_ghz),
    "E07": ("CHSH", "Quatro configurações medem S.", qcs_chsh, leitura_chsh),
    "E08": ("Gerador quântico de números", "H + medição produzem bits aproximadamente equilibrados.", lambda: [qc_qrng()], leitura_qrng),
    "E09": ("Codificação de amplitude", "Ry(2π/3) prepara P(1)=0,75.", lambda: [qc_amplitude()], leitura_amplitude),
    "E10": ("Classificador XOR (VQC)", "Quatro entradas, quatro medições, uma acurácia.", qcs_vqc, leitura_vqc),
    "E11": ("Interferência de dois qubits", "H, CZ e H concentram a distribuição em 00/11.", lambda: [qc_interferencia2()], leitura_interferencia2),
    "E12": ("QFT de 3 qubits", "A transformada de Fourier quântica uniformiza a saída.", lambda: [qc_qft3()], leitura_qft3),
    "E13": ("Produto tensorial |01⟩", "X no qubit 1 prepara |01⟩.", lambda: [qc_tensor01()], leitura_tensor01),
    "E14": ("Ruído de fase", "H-X-H deveria devolver P(0)=1; o backend perde coerência.", lambda: [qc_ruido_phase()], leitura_ruido),
    "E15": ("GHZ via QASM 2.0", "O mesmo GHZ carregado de um texto OpenQASM 2.0.", lambda: [qc_ghz4()], leitura_ghz),
    "E16": ("Esfera de Bloch", "Mede Z e X do estado H|0⟩.", lambda: [qc_superposicao(), qc_basis0()], leitura_bloch),
    "E17": ("Interferência de três qubits", "Uma caminhada curta distribui amplitude em 000/010/101/111.", lambda: [qc_walk3()], leitura_walk3),
    "E18": ("Amostragem binomial", "H + medição; o desvio de P(1) cai com o número de tiros.", lambda: [qc_superposicao()], leitura_amostragem),
}


def circuitos(exp_id: str) -> list[QuantumCircuit]:
    return EXPERIMENTOS[exp_id][2]()


def leitura(exp_id: str, counts: list[dict]) -> str:
    return EXPERIMENTOS[exp_id][3](counts)


# ---------------------------------------------------------------- simulação

def simular(qc: QuantumCircuit, shots: int, rng: np.random.Generator) -> dict[str, int]:
    medidas = []
    for instr in qc.data:
        if instr.operation.name == "measure":
            q = qc.find_bit(instr.qubits[0]).index
            c = qc.find_bit(instr.clbits[0]).index
            medidas.append((q, c))
    limpo = qc.remove_final_measurements(inplace=False)
    probs = Statevector(limpo).probabilities_dict()
    chaves = [str(k) for k in probs]
    pesos = np.array([float(probs[k]) for k in probs], dtype=float)
    pesos = pesos / pesos.sum()
    amostras = rng.choice(chaves, size=shots, p=pesos)
    if not medidas:
        return dict(Counter(str(x) for x in amostras))
    n, m = qc.num_qubits, qc.num_clbits
    counts: Counter[str] = Counter()
    for amostra in amostras:
        s = str(amostra)
        bits = ["0"] * m
        for q, c in medidas:
            bits[m - 1 - c] = s[n - 1 - q]
        counts["".join(bits)] += 1
    return dict(counts)


def rodar_sim(shots: int, seed: int, apenas: list[str] | None) -> None:
    rng = np.random.default_rng(seed)
    for exp_id in (apenas or list(EXPERIMENTOS)):
        nome, desc, _, _ = EXPERIMENTOS[exp_id]
        counts = [simular(qc, shots, rng) for qc in circuitos(exp_id)]
        dados = {
            "id": exp_id, "nome": nome, "descricao": desc,
            "simulado": {"counts": counts, "leitura": leitura(exp_id, counts),
                         "shots": shots, "metodo": "statevector + amostragem"},
            "real": None, "sobreposicao": None, "timestamp": agora(),
        }
        caminho = SAIDA / f"{exp_id}.json"
        anterior = json.loads(caminho.read_text(encoding="utf-8")) if caminho.exists() else {}
        if anterior.get("real"):
            dados["real"] = anterior["real"]
            dados["sobreposicao"] = anterior.get("sobreposicao")
        caminho.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  ✓ {exp_id} {nome}: {dados['simulado']['leitura']}")


def chave_api() -> str:
    chave = os.environ.get("GJQ_API_KEY", "").strip()
    if not chave:
        raise SystemExit("GJQ_API_KEY ausente; defina a chave apenas no ambiente.")
    return chave


def probabilidades(counts: dict[str, int]) -> dict[str, float]:
    total = sum(counts.values())
    return {k: v / total for k, v in counts.items()} if total else {}


def sobreposicao(a: dict[str, int], b: dict[str, int]) -> float:
    pa, pb = probabilidades(a), probabilidades(b)
    return sum(min(pa.get(k, 0.0), pb.get(k, 0.0)) for k in set(pa) | set(pb))


def sobreposicao_lista(a: list[dict], b: list[dict]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(sobreposicao(x, y) for x, y in zip(a, b)) / len(a)


def rodar_real(backend_nome: str, shots: int, timeout: float, seed: int,
               nivel: int, apenas: list[str] | None) -> None:
    from gjq_client import GJQRuntimeService, Sampler, generate_preset_pass_manager

    servico = GJQRuntimeService(api_key=chave_api())
    backend = servico.backend(backend_nome)
    pm = generate_preset_pass_manager(backend=backend, optimization_level=nivel,
                                      seed_transpiler=seed)
    for exp_id in (apenas or list(EXPERIMENTOS)):
        nome, _, _, _ = EXPERIMENTOS[exp_id]
        caminho = SAIDA / f"{exp_id}.json"
        if not caminho.exists():
            raise SystemExit(f"Rode --sim antes de --real ({exp_id} sem JSON).")
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        if dados.get("real") and dados["real"].get("backend") == backend_nome:
            print(f"  · {exp_id} já tem resultado real em {backend_nome}; pulando.")
            continue
        try:
            counts, task_ids = [], []
            for qc in circuitos(exp_id):
                job = Sampler(backend=backend).run(pm.run(qc), shots=shots)
                task_ids.append(getattr(job, "_job_id", None))
                counts.append({str(k): int(v) for k, v in dict(
                    job.result(timeout=timeout)["counts"]).items()})
            dados["real"] = {"counts": counts, "leitura": leitura(exp_id, counts),
                             "task_ids": task_ids, "backend": backend.name,
                             "shots": shots, "timestamp": agora()}
            if dados.get("simulado"):
                dados["sobreposicao"] = sobreposicao_lista(dados["simulado"]["counts"], counts)
            caminho.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  ✓ {exp_id} {nome}: {dados['real']['leitura']}")
        except Exception as exc:
            dados["real_erro"] = f"{type(exc).__name__}: {exc}"
            caminho.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  ✗ {exp_id} falhou: {type(exc).__name__}: {exc}", file=sys.stderr)


def relatorio() -> None:
    def celula(texto) -> str:
        return str(texto).replace("|", "&#124;")

    linhas = ["# Relatório dos 18 experimentos", "",
              "| ID | Experimento | Simulado | Backend | Sobreposição |",
              "|---|---|---|---|---:|"]
    csv_linhas = [["id", "experimento", "simulado", "backend", "sobreposicao"]]
    for exp_id, (nome, _, _, _) in EXPERIMENTOS.items():
        caminho = SAIDA / f"{exp_id}.json"
        d = json.loads(caminho.read_text(encoding="utf-8")) if caminho.exists() else {}
        sim = (d.get("simulado") or {}).get("leitura", "—")
        real = (d.get("real") or {}).get("leitura", "—")
        ov = d.get("sobreposicao")
        ov_txt = f"{ov:.1%}" if isinstance(ov, (int, float)) else "—"
        linhas.append(
            f"| {exp_id} | {celula(nome)} | {celula(sim)} | "
            f"{celula(real)} | {ov_txt} |"
        )
        csv_linhas.append([exp_id, nome, sim, real, ov_txt])
    (SAIDA / "RELATORIO_EXPERIMENTOS.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    with (SAIDA / "experimentos.csv").open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(csv_linhas)
    print(f"Relatório: {SAIDA / 'RELATORIO_EXPERIMENTOS.md'}")
    print(f"CSV: {SAIDA / 'experimentos.csv'}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sim", action="store_true")
    ap.add_argument("--real", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--backend", default="Guoji08")
    ap.add_argument("--shots", type=int, default=1024)
    ap.add_argument("--timeout", type=float, default=900.0)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--optimization-level", type=int, default=2, choices=[0, 1, 2, 3])
    ap.add_argument("--only", nargs="+", choices=list(EXPERIMENTOS), default=None)
    args = ap.parse_args()

    if args.dry_run:
        print(f"Experimentos: {len(EXPERIMENTOS)} | shots: {args.shots}")
        for exp_id in EXPERIMENTOS:
            print(f"  {exp_id} {EXPERIMENTOS[exp_id][0]}: {len(circuitos(exp_id))} circuito(s)")
        print("Circuitos válidos; nenhuma submissão foi feita.")
        return 0
    if not (args.sim or args.real or args.all or args.report):
        ap.print_help()
        return 2
    if args.sim or args.all:
        print("== simulação ==")
        rodar_sim(args.shots, args.seed, args.only)
    if args.real or args.all:
        print("== backend ==")
        rodar_real(args.backend, args.shots, args.timeout, args.seed,
                   args.optimization_level, args.only)
    if args.report:
        relatorio()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
