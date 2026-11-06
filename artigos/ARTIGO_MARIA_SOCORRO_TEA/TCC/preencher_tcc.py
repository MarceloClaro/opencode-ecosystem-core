#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Preenche os placeholders da capa/folha de rosto do TCC e recompila.

Uso:
  python3 preencher_tcc.py \
    --instituicao "Universidade ..." \
    --curso "Curso de ..." \
    --cidade "Cidade/UF" \
    --orientador "Nome do(a) orientador(a)" \
    --titulo "Título a obter"

Não use dados de outra pessoa. O script não valida vínculo institucional.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
ARQUIVOS = [BASE / "TCC_PRETEXTUAL.tex", BASE / "TCC_PRETEXTUAL.md"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--instituicao", required=True)
    ap.add_argument("--curso", required=True)
    ap.add_argument("--cidade", required=True)
    ap.add_argument("--orientador", required=False, default="")
    ap.add_argument("--titulo", required=True)
    args = ap.parse_args()

    mapa = {
        "[INSTITUIÇÃO DE ENSINO]": args.instituicao,
        "[CURSO]": args.curso,
        "[CIDADE]": args.cidade,
        "[NOME DO ORIENTADOR(A)]": args.orientador,
        "[TÍTULO A OBTER]": args.titulo,
    }
    for arquivo in ARQUIVOS:
        texto = arquivo.read_text(encoding="utf-8")
        for antigo, novo in mapa.items():
            texto = texto.replace(antigo, novo)
        arquivo.write_text(texto, encoding="utf-8")
        print("preenchido:", arquivo.name)

    proc = subprocess.run([sys.executable, str(BASE / "build_tcc.py")], cwd=str(BASE))
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
