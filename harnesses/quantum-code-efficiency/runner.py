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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent / "resultados")
    ap.add_argument("--quick", action="store_true", help="mesmo conjunto, sem alterar o protocolo")
    args = ap.parse_args()

    dados = rodar_tudo(seed=args.seed, apenas=args.only)
    json_path, md_path = escrever_relatorio(dados, args.out)
    print(json.dumps(dados["resumo"], indent=2, ensure_ascii=False))
    print(f"JSON: {json_path}")
    print(f"RELATÓRIO: {md_path}")
    return 0 if dados["resumo"]["fail"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
