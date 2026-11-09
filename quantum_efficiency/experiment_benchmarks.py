#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Carrega os circuitos E01–E18 do livro como benchmarks."""
from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
LIVRO = RAIZ / "educacao_quantica_bohm" / "livro_pixel"
if str(LIVRO) not in sys.path:
    sys.path.insert(0, str(LIVRO))

from base.base_experimentos import EXPERIMENTOS, circuitos  # noqa: E402


def benchmarks_experimentos() -> list[dict]:
    """Um item por circuito; E07, E10 e E16 têm mais de um."""
    saida = []
    for exp_id in sorted(EXPERIMENTOS):
        exp = EXPERIMENTOS[exp_id]
        for indice, qc in enumerate(circuitos(exp_id), start=1):
            saida.append({
                "name": f"{exp_id}_{indice}",
                "experiment": exp_id,
                "description": exp["nome"],
                "circuit": qc,
                "coupling_map": None,
            })
    return saida
