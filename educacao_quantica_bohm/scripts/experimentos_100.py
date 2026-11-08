#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Executa os 18 experimentos-base (simulado e backend) dos 100 conceitos.

- simulação: statevector + amostragem de 1024 tiros;
- backend: `gjq-client`, com task IDs e counts;
- sobreposição: `sum_b min(p_sim[b], p_real[b])`, uma medida de semelhança
  entre distribuições (não é fidelidade de estado).

A API key é lida somente de `GJQ_API_KEY`. O script nunca grava a chave.

Uso:
    python .../experimentos_100.py --sim
    python .../experimentos_100.py --real --backend Guoji08
    python .../experimentos_100.py --all --backend Guoji08
    python .../experimentos_100.py --report
    python .../experimentos_100.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np
from qiskit import qasm2
from qiskit.quantum_info import Statevector

RAIZ = Path(__file__).resolve().parents[1]
LIVRO = RAIZ / "livro_pixel"
sys.path.insert(0, str(LIVRO))

from base.base_conceitos import CONCEITOS  # noqa: E402
from base.base_experimentos import EXPERIMENTOS, MAPA, circuitos, leitura  # noqa: E402

SAIDA = RAIZ / "dados_experimentos"
SAIDA.mkdir(parents=True, exist_ok=True)
QASM_GHZ = RAIZ / "circuitos_qasm" / "ghz4.qasm"


def agora() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def _json(caminho: Path) -> dict | None:
    if not caminho.exists():
        return None
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except Exception:
        return None


def contagens_limpas(counts) -> dict[str, int]:
    return {str(k): int(v) for k, v in dict(counts).items()}


def _celula(texto) -> str:
    return str(texto).replace("|", "&#124;")


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


def simular(qc, shots: int, rng: np.random.Generator) -> dict[str, int]:
    """Simula o circuito e devolve counts **nos bits clássicos medidos**.

    `Statevector.probabilities_dict()` devolve o estado de todos os qubits.
    Quando o circuito mede só parte deles (por exemplo, o VQC mede q0), é
    preciso marginalizar para não inventar um bit clássico que não existe.
    """
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


def rodar_sim(shots: int, seed: int, apenas: list[str] | None = None) -> None:
    rng = np.random.default_rng(seed)
    ids = apenas or list(EXPERIMENTOS)
    for exp_id in ids:
        exp = EXPERIMENTOS[exp_id]
        counts = [simular(qc, shots, rng) for qc in circuitos(exp_id)]
        dados = {
            "id": exp_id,
            "nome": exp["nome"],
            "descricao": exp["descricao"],
            "conceitos": [c["id"] for c in CONCEITOS if MAPA[c["id"]] == exp_id],
            "simulado": {
                "counts": counts,
                "leitura": leitura(exp_id, counts),
                "shots": shots,
                "metodo": "statevector + amostragem",
            },
            "real": None,
            "sobreposicao": None,
            "timestamp": agora(),
        }
        caminho = SAIDA / f"{exp_id}.json"
        anterior = _json(caminho) or {}
        if anterior.get("real"):
            dados["real"] = anterior["real"]
            dados["sobreposicao"] = anterior.get("sobreposicao")
        caminho.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  ✓ {exp_id} {exp['nome']}: {dados['simulado']['leitura']}")


def chave_api() -> str:
    chave = os.environ.get("GJQ_API_KEY", "").strip()
    if not chave:
        raise SystemExit("GJQ_API_KEY ausente; defina a chave apenas no ambiente.")
    return chave


def _reuso(exp_id: str, backend_nome: str) -> list[dict] | None:
    """Reaproveita resultados já obtidos, quando o backend coincide."""
    D = RAIZ / "dados_hardware"
    mapa = {
        "E06": ("ghz4_guoji08.json", "counts"),
        "E15": ("ghz4_qasm_guoji08.json", "counts"),
    }
    if exp_id in mapa:
        nome, chave = mapa[exp_id]
        d = _json(D / nome)
        if d and d.get("backend") == backend_nome:
            return [contagens_limpas(d[chave])]
        return None
    if exp_id == "E07":
        d = _json(D / "chsh_guoji08.json")
        if d and d.get("backend") == backend_nome:
            return [contagens_limpas(d["counts"][k]) for k in ("E00", "E01", "E10", "E11")]
        return None
    if exp_id == "E10":
        d = _json(D / "vqc_xor_guoji08.json")
        if d and d.get("backend") == backend_nome:
            return [contagens_limpas(r["counts"]) for r in d["resultados"]]
        return None
    return None


def rodar_real(
    backend_nome: str,
    shots: int,
    timeout: float,
    seed: int,
    nivel: int,
    apenas: list[str] | None = None,
    reusar: bool = True,
) -> None:
    from gjq_client import GJQRuntimeService, Sampler, generate_preset_pass_manager

    servico = GJQRuntimeService(api_key=chave_api())
    backend = servico.backend(backend_nome)
    pm = generate_preset_pass_manager(
        backend=backend, optimization_level=nivel, seed_transpiler=seed
    )
    ids = apenas or list(EXPERIMENTOS)

    for exp_id in ids:
        exp = EXPERIMENTOS[exp_id]
        caminho = SAIDA / f"{exp_id}.json"
        dados = _json(caminho)
        if not dados:
            raise SystemExit(f"Rode --sim antes de --real ({exp_id} sem JSON).")
        if dados.get("real") and dados["real"].get("backend") == backend_nome:
            print(f"  · {exp_id} já tem resultado real em {backend_nome}; pulando.")
            continue

        try:
            counts = _reuso(exp_id, backend_nome) if reusar else None
            task_ids = []
            if counts is None:
                counts = []
                for qc in circuitos(exp_id):
                    isa = pm.run(qc)
                    job = Sampler(backend=backend).run(isa, shots=shots)
                    task_ids.append(getattr(job, "_job_id", None))
                    counts.append(contagens_limpas(job.result(timeout=timeout)["counts"]))
            else:
                print(f"  · {exp_id}: reutilizando resultado existente de {backend_nome}")

            dados["real"] = {
                "counts": counts,
                "leitura": leitura(exp_id, counts),
                "task_ids": task_ids,
                "backend": backend.name,
                "shots": shots,
                "timestamp": agora(),
            }
            dados.pop("real_erro", None)
            if dados.get("simulado"):
                dados["sobreposicao"] = sobreposicao_lista(
                    dados["simulado"]["counts"], counts
                )
            caminho.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  ✓ {exp_id} {exp['nome']}: {dados['real']['leitura']}")
        except Exception as exc:
            dados["real_erro"] = f"{type(exc).__name__}: {exc}"
            caminho.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  ✗ {exp_id} falhou: {type(exc).__name__}: {exc}", file=sys.stderr)


def relatorio() -> None:
    linhas = [
        "# Relatório dos experimentos: 100 conceitos, 18 circuitos",
        "",
        "Cada conceito aponta para um circuito-base. A coluna **sobreposição**",
        "compara a distribuição simulada com a do backend; não é fidelidade de",
        "estado nem prova de emaranhamento.",
        "",
        "## Experimentos-base",
        "",
        "| ID | Experimento | Simulado | Backend | Sobreposição |",
        "|---|---|---|---|---:|",
    ]
    for exp_id, exp in EXPERIMENTOS.items():
        d = _json(SAIDA / f"{exp_id}.json") or {}
        sim = (d.get("simulado") or {}).get("leitura", "—").replace(".", ",")
        real = (d.get("real") or {}).get("leitura", "—").replace(".", ",")
        ov = d.get("sobreposicao")
        ov_txt = f"{ov:.1%}".replace(".", ",") if isinstance(ov, (int, float)) else "—"
        linhas.append(
            f"| {exp_id} | {_celula(exp['nome'])} | {_celula(sim)} | "
            f"{_celula(real)} | {ov_txt} |"
        )

    linhas += [
        "",
        "## Cobertura dos 100 conceitos",
        "",
        "::: {.tabela-longa}",
        "",
        "| Conceito | Experimento | Simulado | Backend | Sobreposição |",
        "|---|---|---|---|---:|",
    ]
    for c in CONCEITOS:
        exp_id = MAPA[c["id"]]
        d = _json(SAIDA / f"{exp_id}.json") or {}
        sim = (d.get("simulado") or {}).get("leitura", "—").replace(".", ",")
        real = (d.get("real") or {}).get("leitura", "—").replace(".", ",")
        ov = d.get("sobreposicao")
        ov_txt = f"{ov:.1%}".replace(".", ",") if isinstance(ov, (int, float)) else "—"
        linhas.append(
            f"| {_celula(c['titulo'])} | {exp_id} — "
            f"{_celula(EXPERIMENTOS[exp_id]['nome'])} | "
            f"{_celula(sim)} | {_celula(real)} | {ov_txt} |"
        )
    linhas += [
        "",
        ":::",
        "",
        "> **Limite:** a sobreposição mede semelhança entre distribuições de",
        "> counts. Ela cai com ruído e com o tamanho da amostra, mas não prova",
        "> que o estado preparado é puro, emaranhado ou fiel ao ideal.",
        "",
    ]
    caminho = SAIDA / "RELATORIO_EXPERIMENTOS.md"
    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"Relatório: {caminho}")


def dry_run(shots: int) -> int:
    print(f"Experimentos: {len(EXPERIMENTOS)} | conceitos: {len(MAPA)} | shots: {shots}")
    for exp_id, exp in EXPERIMENTOS.items():
        cs = circuitos(exp_id)
        print(
            f"  {exp_id} {exp['nome']}: {len(cs)} circuito(s), "
            f"qubits={[c.num_qubits for c in cs]}"
        )
    print("Circuitos válidos; nenhuma submissão foi feita.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sim", action="store_true", help="roda a simulação local")
    ap.add_argument("--real", action="store_true", help="roda no backend")
    ap.add_argument("--all", action="store_true", help="simulação + backend")
    ap.add_argument("--report", action="store_true", help="gera o relatório Markdown")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--backend", default="Guoji08")
    ap.add_argument("--shots", type=int, default=1024)
    ap.add_argument("--timeout", type=float, default=900.0)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--optimization-level", type=int, default=2, choices=[0, 1, 2, 3])
    ap.add_argument("--only", nargs="+", choices=list(EXPERIMENTOS), default=None)
    ap.add_argument("--no-reuse", action="store_true")
    args = ap.parse_args()

    if args.dry_run:
        return dry_run(args.shots)
    if not (args.sim or args.real or args.all or args.report):
        ap.print_help()
        return 2
    if args.shots <= 0:
        raise SystemExit("--shots deve ser positivo")

    if args.sim or args.all:
        print("== simulação ==")
        rodar_sim(args.shots, args.seed, args.only)
    if args.real or args.all:
        print("== backend ==")
        rodar_real(
            args.backend, args.shots, args.timeout, args.seed,
            args.optimization_level, args.only, not args.no_reuse,
        )
    if args.report:
        relatorio()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())