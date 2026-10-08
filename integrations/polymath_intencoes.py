# -*- coding: utf-8 -*-
"""Intenções de federação polímata (SPEC-935-R716).

Importa proposta R715 como intenções aguardando humano. Nenhuma auto-federação:
aprovada significa pronta para análise R621 com artefato local, nunca federada.
Sem rede, sem instalação, sem escrita fora do diretório de intenções.
"""
from __future__ import annotations

import copy
import datetime
import json
import os
import secrets
from typing import Any, Dict

SPEC_ID = "SPEC-935-R716"
GERADOR = "marceloclaro"


def _agora() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def importar(proposta_path: str, destino_dir: str) -> Dict[str, Any]:
    """Importa somente decisoes proposto como intenções aguardando_humano."""
    if not isinstance(proposta_path, str) or not proposta_path.strip():
        raise ValueError("proposta_path vazio (fail-closed).")
    if not isinstance(destino_dir, str) or not destino_dir.strip():
        raise ValueError("destino_dir vazio (fail-closed).")
    with open(proposta_path, encoding="utf-8") as fh:
        proposta = json.load(fh)
    decisoes = proposta.get("decisoes", [])
    if not isinstance(decisoes, list):
        raise ValueError("proposta sem decisoes.")
    os.makedirs(destino_dir, exist_ok=True)
    intencoes, retidas = [], []
    for d in decisoes:
        url = str(d.get("url", ""))
        if str(d.get("decisao")) != "proposto":
            retidas.append({"url": url, "motivo": str(d.get("motivo", ""))})
            continue
        intencoes.append({
            "intencao_id": "INT-" + secrets.token_hex(4).upper(),
            "url": url, "classe": d.get("classe"), "motivo_proposta": str(d.get("motivo", "")),
            "licenca": d.get("licenca"), "status": "aguardando_humano",
            "pronta_para_federacao": False, "exige_artefato_local": True,
            "importada_em": _agora(),
        })
    payload = {"spec_id": SPEC_ID, "gerador": GERADOR, "gerado_em": _agora(),
               "origem_proposta": os.path.abspath(proposta_path),
               "total": len(intencoes), "intencoes": intencoes,
               "retidas_informativas": retidas,
               "rotulo": "candidato_a_inspecao", "exige_validacao_externa": True}
    with open(os.path.join(destino_dir, "intencoes.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    with open(os.path.join(destino_dir, "decisoes_humanas.jsonl"), "a", encoding="utf-8") as fh:
        pass
    return {"ok": True, "destino": destino_dir, "intencoes": len(intencoes),
            "retidas_informativas": len(retidas)}


def _carregar(destino_dir: str) -> Dict[str, Any]:
    with open(os.path.join(destino_dir, "intencoes.json"), encoding="utf-8") as fh:
        return json.load(fh)


def _salvar(destino_dir: str, payload: Dict[str, Any]) -> None:
    with open(os.path.join(destino_dir, "intencoes.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)


def decidir(destino_dir: str, url: str, decisao: str, humano: bool,
            motivo: str, responsavel: str) -> Dict[str, Any]:
    """Aprova/rejeita uma intenção. Humano True literal exigido."""
    if humano is not True:
        raise ValueError("Decisão exige humano=true explícito (R716).")
    if decisao not in ("aprovada", "rejeitada"):
        raise ValueError("decisao deve ser aprovada ou rejeitada.")
    if not isinstance(motivo, str) or not motivo.strip():
        raise ValueError("motivo vazio (fail-closed).")
    if not isinstance(responsavel, str) or not responsavel.strip():
        raise ValueError("responsavel vazio (fail-closed).")
    payload = _carregar(destino_dir)
    alvo = next((i for i in payload.get("intencoes", []) if str(i.get("url", "")).lower() == str(url).lower()), None)
    if alvo is None:
        raise ValueError(f"URL sem intenção (retida ou desconhecida): {url!r}.")
    if alvo.get("status") != "aguardando_humano":
        raise ValueError(f"Intenção já decidida ({alvo.get('status')}), lote abortado: {url!r}.")
    alvo["status"] = decisao
    alvo["pronta_para_federacao"] = False
    alvo["exige_artefato_local"] = True
    alvo["decidida_por"] = responsavel
    alvo["decidida_em"] = _agora()
    alvo["motivo_decisao"] = motivo
    _salvar(destino_dir, payload)
    with open(os.path.join(destino_dir, "decisoes_humanas.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"quando": alvo["decidida_em"], "url": alvo["url"],
                             "decisao": decisao, "responsavel": responsavel,
                             "motivo": motivo}, ensure_ascii=False) + "\n")
    return copy.deepcopy(alvo)


def resumo(destino_dir: str) -> Dict[str, Any]:
    """Contabiliza intenções sem efeitos colaterais."""
    payload = _carregar(destino_dir)
    itens = payload.get("intencoes", [])
    conta = lambda s: sum(1 for i in itens if i.get("status") == s)
    return {"total": len(itens), "aguardando": conta("aguardando_humano"),
            "aprovadas": conta("aprovada"), "rejeitadas": conta("rejeitada"),
            "retidas_informativas": len(payload.get("retidas_informativas", [])),
            "rotulo": "candidato_a_inspecao"}
