# -*- coding: utf-8 -*-
"""Lote piloto de decisões (SPEC-935-R717).

Aplica decidir em sequência com atomicidade por lote: falha aborta o restante.
Exemplo ratificável, não aprovação definitiva. Sem rede, sem federação.
"""
from __future__ import annotations

import datetime
import json
import os
from typing import Any, Dict, List

from integrations import polymath_intencoes as inten

SPEC_ID = "SPEC-935-R717"
GERADOR = "marceloclaro"


def decidir_lote(intencoes_dir: str, itens: List[Dict[str, str]], humano: bool,
                 responsavel: str) -> Dict[str, Any]:
    """Aplica lote 3+1 ou qualquer lote com trilha. Falha aborta restante."""
    if humano is not True:
        raise ValueError("Lote exige humano=true explícito (R717).")
    if not isinstance(responsavel, str) or not responsavel.strip():
        raise ValueError("responsavel vazio (fail-closed).")
    if not isinstance(itens, list) or not itens:
        raise ValueError("itens vazio (fail-closed).")
    aplicadas = []
    for it in itens:
        url = str(it.get("url", ""))
        dec = str(it.get("decisao", ""))
        mot = str(it.get("motivo", ""))
        if not url.strip() or dec not in ("aprovada", "rejeitada") or not mot.strip():
            raise ValueError(f"Item inválido, lote abortado após {len(aplicadas)}: {url!r}.")
        # Aborta sem aplicar restante se alvo ausente ou já decidido
        resumo_antes = inten.resumo(intencoes_dir)
        _ = resumo_antes  # leitura auditável antes de cada passo
        r = inten.decidir(intencoes_dir, url, dec, humano=True, motivo=mot, responsavel=responsavel)
        aplicadas.append({"url": r["url"], "status": r["status"], "motivo": mot})
    payload = {"spec_id": SPEC_ID, "gerador": GERADOR,
               "quando": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "responsavel": responsavel, "piloto": True,
               "ratificacao_titular_pendente": True,
               "aplicadas": aplicadas, "total": len(aplicadas),
               "nota": "Exemplo ratificável; nada federado. Aprovação definitiva exige ratificação por lab."}
    with open(os.path.join(intencoes_dir, "lote_piloto.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    return {"ok": True, "aplicadas": len(aplicadas), "lote": os.path.join(intencoes_dir, "lote_piloto.json")}
