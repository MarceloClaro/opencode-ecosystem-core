# -*- coding: utf-8 -*-
"""Vigia de frescor dos pins (SPEC-935-R745).

Compara pushed_at contra a janela da classe com `agora` injetável.
Sem rede, sem decisão, sem federação.
"""
from __future__ import annotations

import copy
import datetime
import json
import os
from typing import Any, Dict, List

SPEC_ID = "SPEC-935-R745"
GERADOR = "marceloclaro"
LIMIAR_AVISO_DIAS = 7


def _parse_iso(s: Any) -> datetime.datetime | None:
    if not isinstance(s, str) or not s.strip():
        return None
    try:
        dt = datetime.datetime.fromisoformat(s.strip().replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=datetime.timezone.utc)
    except ValueError:
        return None


def verificar(pins: List[Dict[str, Any]], janelas: Dict[str, int],
              agora: datetime.datetime | None = None) -> Dict[str, Any]:
    """Classifica cada pin em ok|aviso_7d|vencido|sem_dados."""
    agora = agora or datetime.datetime.now(datetime.timezone.utc)
    norm_jan = {str(k).lower(): int(v) for k, v in (janelas or {}).items()}
    itens = []
    for p in pins:
        url = str(p.get("url", ""))
        dt = _parse_iso(p.get("pushed_at"))
        janela = norm_jan.get(url.lower())
        if dt is None or janela is None:
            itens.append({"url": url, "estado": "sem_dados", "janela_dias": janela})
            continue
        idade = (agora - dt).days
        restantes = janela - idade
        estado = "vencido" if restantes < 0 else ("aviso_7d" if restantes <= LIMIAR_AVISO_DIAS else "ok")
        itens.append({"url": url, "idade_dias": idade, "janela_dias": janela,
                      "dias_restantes": restantes, "estado": estado})
    conta = lambda e: sum(1 for i in itens if i["estado"] == e)
    return {"spec_id": SPEC_ID, "gerador": GERADOR, "total": len(itens),
            "ok": conta("ok"), "avisos": conta("aviso_7d"), "vencidos": conta("vencido"),
            "sem_dados": conta("sem_dados"), "itens": itens,
            "rotulo": "candidato_a_inspecao"}


def emitir_relatorio(destino_dir: str, relatorio: Dict[str, Any]) -> Dict[str, Any]:
    """Escreve vigia.json."""
    os.makedirs(destino_dir, exist_ok=True)
    alvo = os.path.join(destino_dir, "vigia.json")
    with open(alvo, "w", encoding="utf-8") as fh:
        json.dump(copy.deepcopy(relatorio), fh, ensure_ascii=False, indent=2)
    return {"ok": True, "arquivo": alvo}
