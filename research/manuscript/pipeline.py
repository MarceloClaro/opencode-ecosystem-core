# -*- coding: utf-8 -*-
"""Orquestração de produção: um artigo ou lote (SPEC-935-R706, AC5).

O conteúdo científico vem do chamador (orquestrador/LLM) via `conteudo`:
{ nome_do_modulo: texto_latex }. O motor monta, valida e manifesta.
"""
from __future__ import annotations

import os
from typing import Any

from research.manuscript.config import ArticleConfig
from research.manuscript.scaffold import scaffold_workspace
from research.manuscript.gates import run_gates


def produzir(config: ArticleConfig, conteudo: dict[str, str] | None = None,
             force: bool = False) -> dict[str, Any]:
    """Scaffold + injeta conteúdo (se dado) + gates + manifesto. Um workspace por artigo."""
    saida = scaffold_workspace(config, force=force)
    ws = saida["workspace"]
    injetados = 0
    for modulo, texto in (conteudo or {}).items():
        caminho = os.path.join(ws, "modulos", f"{modulo}.tex")
        if os.path.isfile(caminho):
            with open(caminho, "w", encoding="utf-8") as fh:
                fh.write(texto)
            injetados += 1
    from integrations.artigo_academico_mcp import _tool_emitir_manifesto
    man = _tool_emitir_manifesto(ws, "1.0")
    gates = run_gates(ws)
    saida.update({"injetados": injetados,
                  "manifesto_ok": man.get("ok", False),
                  "gates": gates})
    return saida


def produzir_lote(configs: list[ArticleConfig],
                  conteudos: list[dict[str, str] | None] | None = None,
                  force: bool = False) -> dict[str, Any]:
    """N artigos em sequência, um workspace isolado por artigo + tabela-resumo."""
    if conteudos is None:
        conteudos = [None] * len(configs)
    if len(conteudos) != len(configs):
        raise ValueError("conteudos deve ter o mesmo tamanho de configs.")
    resultados = []
    for cfg, cont in zip(configs, conteudos):
        try:
            r = produzir(cfg, cont, force=force)
            g = r.get("gates", {})
            resultados.append({"slug": cfg.slug, "titulo": cfg.titulo,
                               "ok": True, "artefatos": g.get("artefatos", {}).get("total", 0),
                               "citacoes_prontas": g.get("citacoes", {}).get("pronto", False),
                               "achados_alegacao": g.get("alegacoes", {}).get("total", 0)})
        except Exception as exc:  # isolamento: falha de um não derruba o lote
            resultados.append({"slug": cfg.slug, "titulo": cfg.titulo,
                               "ok": False, "erro": f"{type(exc).__name__}: {exc}"})
    return {"ok": True, "total": len(resultados),
            "concluidos": sum(1 for r in resultados if r["ok"]),
            "resultados": resultados}
