# -*- coding: utf-8 -*-
"""Gates uniformes do pipeline (SPEC-935-R706, AC4).

Reutiliza as implementações canônicas (sem duplicar lógica):
- citações: integrations.artigo_academico_mcp._tool_verificar_citacoes
- força de alegação: research.claim_strength.guard.auditar
- artefatos: integrations.artigo_academico_mcp._tool_pipeline_status
"""
from __future__ import annotations

import os
from typing import Any


def run_gates(diretorio: str, texto: str = "") -> dict[str, Any]:
    """Executa os 3 gates sobre um workspace. Fail-closed em diretório inexistente."""
    if not os.path.isdir(diretorio):
        return {"ok": False, "error": f"Diretório inexistente: {diretorio}."}
    from integrations.artigo_academico_mcp import (
        _tool_pipeline_status, _tool_verificar_citacoes,
    )
    from research.claim_strength.guard import auditar

    cit = _tool_verificar_citacoes(diretorio)
    art = _tool_pipeline_status(diretorio)
    cla = auditar(texto) if texto.strip() else {
        "ok": True, "frases_analisadas": 0, "achados": [], "total": 0,
        "status": "nao_avaliado",
        "nota_metodo": "Texto não fornecido; gate de alegação pulado.",
    }
    pronto = bool(cit.get("pronto_para_submissao")) and art.get("ok", False)
    return {
        "ok": True,
        "citacoes": {"indefinidas": cit.get("indefinidas", []),
                     "pronto": cit.get("pronto_para_submissao", False)},
        "alegacoes": {"total": cla.get("total", 0), "status": cla.get("status", "")},
        "artefatos": {"total": art.get("total", 0)},
        "pronto_para_submissao": pronto,
    }
