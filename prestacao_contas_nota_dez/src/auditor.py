# -*- coding: utf-8 -*-
"""
Auditor da prestação de contas (Prêmio Escola Nota Dez)
========================================================
Gera checklist a partir das demandas extraídas da diligência e calcula um
SCORE INTERNO de conformidade.

ANTI-OVERCLAIM: o score é medida de cobertura dos apontamentos da diligência
(item parseado → providência registrada → documento comprovatório). Não é e
não pode ser tratado como aprovação do órgão concedente nem como certificação.
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List


def _id_demanda(idx: int, texto: str) -> str:
    digest = hashlib.sha1(texto.encode("utf-8", "ignore")).hexdigest()[:6]
    return f"D{idx + 1:02d}-{digest}"


def _normaliza(texto: str) -> str:
    """Chave de dedup: minúsculas, sem espaços múltiplos, sem pontuação."""
    return "".join(c.lower() for c in texto if c.isalnum() or c.isspace())


def _minimo(item_texto: str) -> bool:
    """Filtro anti-ruído: item curto demais para ser apontamento útil."""
    return len(item_texto.strip()) >= 12


def _mescla_blocos(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Junta blocos com o mesmo título (OCR repete cabeçalhos por página)."""
    vistos: Dict[str, Dict[str, Any]] = {}
    ordem: List[str] = []
    for bloco in doc.get("blocos", []):
        titulo = bloco.get("titulo", "").strip() or "(sem título)"
        if titulo not in vistos:
            vistos[titulo] = {"titulo": titulo, "demandas": [], "metadados": bloco.get("metadados", {})}
            ordem.append(titulo)
        vistos[titulo]["demandas"].extend(bloco.get("demandas", []))
        vistos[titulo]["metadados"].update(bloco.get("metadados", {}) or {})
    return [vistos[t] for t in ordem]


def auditar_diligencia(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Gera o checklist item-a-item, deduplicando demandas repetidas.

    Cada item nasce com status ``pendente``; o executor preenche as colunas
    ``providencia``, ``documento`` e ``status`` (atendido) mediante evidência.

    Além do ``status`` de tramitação, cada item carrega:
    - ``estado_documental``: conferido | incompleto | não localizado no material
      recebido | ilegível | não se aplica, com justificativa | (inicial) não examinado.
    - ``estado_tramitacao``: identificado | em obtenção | minuta preparada |
      correção evidenciada | encaminhado | aceite comprovado pelo órgão.
    """
    checklist: List[Dict[str, Any]] = []
    idx = 0
    vistos: set[str] = set()
    for bloco in _mescla_blocos(doc):
        for demanda in bloco.get("demandas", []):
            texto = demanda.get("texto", "").strip()
            if not texto or not _minimo(texto):
                continue
            chave = _normaliza(texto)
            if chave in vistos:
                continue
            vistos.add(chave)
            item = {
                "id": _id_demanda(idx, texto),
                "bloco": bloco.get("titulo", ""),
                "demanda": texto,
                "pagina": demanda.get("pagina", ""),
                "providencia": "",
                "documento": "",
                "status": "pendente",
                "estado_documental": "não examinado",
                "estado_tramitacao": "identificado",
            }
            checklist.append(item)
            idx += 1
    return checklist


def consolidar_estados(checklist: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    """Agrega contagem por estado (documental e de tramitação)."""
    out: Dict[str, Dict[str, int]] = {"documental": {}, "tramitacao": {}}
    for item in checklist:
        ed = item.get("estado_documental", "não examinado") or "não examinado"
        et = item.get("estado_tramitacao", "identificado") or "identificado"
        out["documental"][ed] = out["documental"].get(ed, 0) + 1
        out["tramitacao"][et] = out["tramitacao"].get(et, 0) + 1
    return out


def calcular_score(checklist: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Cobertura interna: itens com providência + documento sobre o total.

    Um item só conta como ``atendido`` se tiver providência E documento
    comprobatório preenchidos — caso contrário permanece ``pendente``.
    """
    total = len(checklist)
    atendidos = sum(
        1
        for item in checklist
        if item["status"] == "atendido" and item["providencia"].strip() and item["documento"].strip()
    )
    pendentes = total - atendidos
    cobertura = (atendidos / total) if total else 0.0
    return {
        "total": total,
        "atendidos": atendidos,
        "pendentes": pendentes,
        "cobertura": round(cobertura, 4),
    }