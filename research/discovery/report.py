# -*- coding: utf-8 -*-
"""Relato calibrado + pacote de replicação (SPEC-935-R708, AC4/AC5).

Gera seção de resultados com marcadores e bloco obrigatório de limitações.
Linguagem calibrada: 'associado', 'coerente', 'sem evidência' — nunca
'prova', 'cura', 'eficaz' ou 'causa' (exceto desenho causal, fora de escopo).
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone


def secao_resultados(titulo: str, achados: list[dict],
                     limitacoes: list[str]) -> str:
    """Monta markdown de resultados. Exige ao menos 1 limitação declarada."""
    if not limitacoes:
        raise ValueError("Seção de resultados exige ao menos 1 limitação declarada.")
    linhas = [f"## {titulo}", ""]
    for i, a in enumerate(achados, start=1):
        linhas.append(f"### Resultado {i} [RESULTADO]")
        linhas.append("")
        for chave in ("teste", "n", "n1", "n2", "t", "gl", "r", "p", "alfa",
                      "diferenca_medias", "ic95", "cohen_d", "magnitude_d", "leitura"):
            if chave in a:
                linhas.append(f"- {chave}: {a[chave]}")
        linhas.append("")
    linhas.append("### Limitações [OBRIGATÓRIO]")
    linhas.append("")
    for lim in limitacoes:
        linhas.append(f"- {lim}")
    linhas.append("")
    return "\n".join(linhas)


def pacote_replicacao(diretorio: str, dados_nome: str = "dados.csv",
                      metodos: dict | None = None,
                      resultados: dict | None = None) -> dict:
    """Grava dados.csv (hash), methods.json e results.json — trilha mínima."""
    if not os.path.isdir(diretorio):
        raise FileNotFoundError(f"Diretório inexistente: {diretorio}.")
    dados_path = os.path.join(diretorio, dados_nome)
    if not os.path.isfile(dados_path):
        raise FileNotFoundError(f"Dados ausentes: {dados_path}.")
    h = hashlib.sha256()
    with open(dados_path, "rb") as fh:
        for bloco in iter(lambda: fh.read(65536), b""):
            h.update(bloco)
    pacote = {
        "schema_version": "1.0",
        "criado_em": datetime.now(timezone.utc).isoformat(),
        "dados": {"arquivo": dados_nome, "sha256": h.hexdigest()},
        "metodos": metodos or {},
        "resultados": resultados or {},
        "nota": "Replicação exige mesmo ambiente e semente quando aplicável.",
    }
    saida = os.path.join(diretorio, "pacote_replicacao.json")
    with open(saida, "w", encoding="utf-8") as fh:
        json.dump(pacote, fh, ensure_ascii=False, indent=2)
    return {"ok": True, "arquivo": saida, "sha256_dados": h.hexdigest()}
