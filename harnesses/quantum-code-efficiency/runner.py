#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Runner do harness de eficiência de código quântico (R1108)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from quantum_efficiency.harness import rodar_tudo, escrever_relatorio  # noqa: E402
from quantum_efficiency.sweep import (  # noqa: E402
    escrever_relatorio_experimentos,
    varrer_experimentos,
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["synthetic", "experiments", "all"], default="synthetic")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--levels", nargs="*", type=int, default=None)
    ap.add_argument("--noise", nargs="*", type=float, default=None)
    ap.add_argument("--shots-noise", type=int, default=2048)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent / "resultados")
    ap.add_argument("--quick", action="store_true", help="reduz níveis, ruído e shots")
    args = ap.parse_args()

    niveis = tuple(args.levels) if args.levels else ((0, 3) if args.quick else (0, 1, 2, 3))
    ruidos = tuple(args.noise) if args.noise else ((0.0, 0.005) if args.quick else (0.0, 0.001, 0.005, 0.01))
    shots_ruido = 512 if args.quick else args.shots_noise
    falhas = 0

    if args.mode in ("synthetic", "all"):
        dados = rodar_tudo(seed=args.seed, apenas=args.only)
        json_path, md_path = escrever_relatorio(dados, args.out)
        print(json.dumps(dados["resumo"], indent=2, ensure_ascii=False))
        print(f"JSON: {json_path}")
        print(f"RELATÓRIO: {md_path}")
        falhas += dados["resumo"]["fail"]

    if args.mode in ("experiments", "all"):
        dados = varrer_experimentos(
            seed=args.seed,
            niveis=niveis,
            ruidos=ruidos,
            shots=shots_ruido,
            apenas=args.only,
        )
        json_path, md_path = escrever_relatorio_experimentos(dados, args.out)
        print(json.dumps(dados["resumo"], indent=2, ensure_ascii=False))
        print(f"JSON: {json_path}")
        print(f"RELATÓRIO: {md_path}")
        falhas += dados["resumo"]["fail"]

    return 0 if falhas == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
