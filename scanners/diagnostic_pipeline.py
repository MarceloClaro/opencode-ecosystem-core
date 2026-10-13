# -*- coding: utf-8 -*-
"""Pipeline de Diagnóstico por Gaps — auditoria hermética entre artefatos (SPEC-935-R767).

``DiagnosticPipeline.varrer`` é hermético: sem rede, subprocesso, LLM ou
terceiros além da stdlib. Seus resultados carregam
`candidato_a_inspecao + exige_validacao_externa` e não substituem compilação,
testes ou validação externa. A função ``run`` preserva a API do pipeline legado.
"""
from __future__ import annotations

import os
import re
from typing import Any, Dict, List

SPEC_ID = "SPEC-935-R767"
GERADOR = "marceloclaro"
TIPOS = ("nomes", "cobertura")


def _ler(arquivo: str) -> str | None:
    try:
        with open(arquivo, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeError):
        return None


def _nomes(texto: str, regex: str) -> List[str]:
    try:
        padrao = re.compile(regex)
    except re.error as exc:
        raise ValueError(f"regex inválida: {exc}")
    if padrao.groups < 1:
        raise ValueError("regex deve ter ao menos 1 grupo.")
    vistos: List[str] = []
    for m in padrao.finditer(texto):
        nome = m.group(1)
        if nome not in vistos:
            vistos.append(nome)
    return vistos


class DiagnosticPipeline:
    """Audita sincronia entre artefatos declarados em um plano."""

    def varrer(self, plano: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(plano, dict):
            raise ValueError("plano deve ser objeto.")
        conjuntos = plano.get("conjuntos")
        if not isinstance(conjuntos, list) or not conjuntos:
            raise ValueError("plano.conjuntos deve ser lista não vazia.")
        checagens = []
        ids = set()
        for item in conjuntos:
            if not isinstance(item, dict):
                raise ValueError("cada checagem deve ser objeto.")
            cid = item.get("id")
            if not isinstance(cid, str) or not cid.strip():
                raise ValueError("cada checagem deve ter ID textual não vazio.")
            cid = cid.strip()
            if cid in ids:
                raise ValueError(f"ID de checagem duplicado: '{cid}'.")
            ids.add(cid)
            tipo = item.get("tipo")
            if tipo not in TIPOS:
                raise ValueError(f"tipo inválido em '{cid}': {tipo!r}.")
            arquivo = item.get("arquivo")
            regex = item.get("regex")
            if not isinstance(arquivo, str) or not arquivo.strip():
                raise ValueError(f"arquivo ausente em '{cid}'.")
            if not isinstance(regex, str) or not regex.strip():
                raise ValueError(f"regex ausente em '{cid}'.")
            checagens.append((item, cid))

        gaps: List[Dict[str, str]] = []
        total = len(checagens)
        for item, cid in checagens:
            tipo = item["tipo"]
            arquivo = item["arquivo"]
            texto = _ler(arquivo)
            if texto is None:
                gaps.append({"id": cid, "motivo": "arquivo_ausente",
                             "detalhe": arquivo})
                continue
            if tipo == "nomes":
                self._checar_nomes(item, cid, texto, gaps)
            else:
                self._checar_cobertura(item, cid, texto, gaps)
        falharam = len({g["id"] for g in gaps})
        return {
            "spec_id": SPEC_ID,
            "gerador": GERADOR,
            "total_checks": total,
            "passaram": total - falharam,
            "falharam": falharam,
            "gaps": gaps,
            "rotulo": "candidato_a_inspecao",
            "exige_validacao_externa": True,
        }

    def _checar_nomes(self, item: Dict[str, Any], cid: str,
                      texto: str, gaps: List[Dict[str, str]]) -> None:
        esperados = item.get("esperados", [])
        proibidos = item.get("proibidos", [])
        if not isinstance(esperados, list) or not isinstance(proibidos, list):
            raise ValueError(f"esperados/proibidos devem ser listas em '{cid}'.")
        achados = _nomes(texto, item["regex"])
        for nome in esperados:
            if nome not in achados:
                gaps.append({"id": cid, "motivo": "faltante",
                             "detalhe": str(nome)})
        for nome in achados:
            if nome not in [str(e) for e in esperados]:
                gaps.append({"id": cid, "motivo": "excedente",
                             "detalhe": str(nome)})
        for padrao in proibidos:
            try:
                rx = re.compile(str(padrao))
            except re.error as exc:
                raise ValueError(f"regex proibida inválida em '{cid}': {exc}")
            if rx.search(texto):
                gaps.append({"id": cid, "motivo": "proibido",
                             "detalhe": str(padrao)})

    def _checar_cobertura(self, item: Dict[str, Any], cid: str,
                          texto: str, gaps: List[Dict[str, str]]) -> None:
        ref = item.get("referencia")
        if not isinstance(ref, dict) or not isinstance(ref.get("arquivo"), str) \
                or not isinstance(ref.get("regex"), str):
            raise ValueError(f"referencia inválida em '{cid}'.")
        texto_ref = _ler(ref["arquivo"])
        if texto_ref is None:
            gaps.append({"id": cid, "motivo": "arquivo_ausente",
                         "detalhe": str(ref["arquivo"])})
            return
        for nome in _nomes(texto, item["regex"]):
            if nome not in _nomes(texto_ref, ref["regex"]):
                gaps.append({"id": cid, "motivo": "cobertura",
                             "detalhe": str(nome)})


def run(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    """Preserva a API do scanner legado quando este submódulo é importado.

    A importação de ``scanners.diagnostic_pipeline`` substitui o atributo
    homônimo do pacote por este módulo. O diagnóstico por gaps continua em
    ``DiagnosticPipeline.varrer``; ``run`` mantém a chamada do pipeline original.
    """
    from scanners.pipeline import diagnostic_pipeline as legacy_pipeline

    return legacy_pipeline.run(*args, **kwargs)
