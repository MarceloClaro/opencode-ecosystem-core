# -*- coding: utf-8 -*-
"""
Verificação documental base (referências do plugin contas-escolares-airam-veras)
=================================================================================
Carrega `references/checklist-base.csv` (C01–C40) como lista **adaptável** de
verificações documentais de prestação de contas do Prêmio Escola Nota Dez.

ANTI-OVERCLAIM: o checklist-base é um ponto de partida para conferência, não uma
declaração de obrigações universais nem um laudo de conformidade. Cada verificação
precisa ser ajustada ao programa, exercício, parcela e regime aplicáveis.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

_REFERENCIAS = Path(__file__).resolve().parent.parent / "references"


def carregar_checklist_base(caminho: Path | None = None) -> List[Dict[str, str]]:
    """Lê o CSV de verificações base (separador `;`) e devolve lista de dicts."""
    fonte = Path(caminho) if caminho else _REFERENCIAS / "checklist-base.csv"
    if not fonte.exists():
        raise FileNotFoundError(f"checklist-base.csv não encontrado: {fonte}")
    itens: List[Dict[str, str]] = []
    with open(fonte, encoding="utf-8") as fh:
        for linha in csv.DictReader(fh, delimiter=";"):
            if linha.get("id"):
                itens.append(
                    {
                        "id": linha.get("id", "").strip(),
                        "grupo": linha.get("grupo", "").strip(),
                        "verificacao": linha.get("verificacao", "").strip(),
                        "condicao": linha.get("condicao", "").strip(),
                        "referencia_historica": linha.get("referencia_historica", "").strip(),
                    }
                )
    return itens


def grupos_disponiveis(itens: List[Dict[str, str]]) -> List[str]:
    grupos: List[str] = []
    for item in itens:
        if item["grupo"] and item["grupo"] not in grupos:
            grupos.append(item["grupo"])
    return grupos


def gerar_tabela_base(itens: List[Dict[str, str]]) -> str:
    """Markdown resumido das verificações (id | grupo | verificação | condição)."""
    linhas = ["| ID | Grupo | Verificação | Condição |", "| --- | --- | --- | --- |"]
    for item in itens:
        linhas.append(
            f"| {item['id']} | {item['grupo']} | {item['verificacao']} | {item['condicao']} |"
        )
    return "\n".join(linhas)