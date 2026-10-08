# -*- coding: utf-8 -*-
"""Dossiê consolidado sem decidir (SPEC-935-R723).

Coleta artefatos do piloto com hashes e resume pendências titulares.
Sem rede, subprocesso ou federação.
"""
from __future__ import annotations

import copy
import datetime
import hashlib
import json
import os
from typing import Any, Dict, List

SPEC_ID = "SPEC-935-R723"
GERADOR = "marceloclaro"
ARTEFATOS = ["intencoes.json", "lote_piloto.json", "readiness.json",
             "relatorio_autonomo.json", "minuta_r621.json", "pareceres.json",
             "decisoes_humanas.jsonl"]
SPECS = ["SPEC-935-R711-pesquisador-polimata-github.md", "SPEC-935-R712-polimata-superficies.md",
         "SPEC-935-R713-pinagem-viva-federacao.md", "SPEC-935-R714-executor-vivo-pinagem.md",
         "SPEC-935-R715-federacao-classes.md", "SPEC-935-R716-intencoes-federacao.md",
         "SPEC-935-R717-lote-piloto.md", "SPEC-935-R718-readiness.md",
         "SPEC-935-R720-inventario-autonomo.md", "SPEC-935-R721-minuta.md",
         "SPEC-935-R722-parecer.md", "SPEC-935-R723-dossie.md"]


def _sha(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(65536), b""):
            h.update(b)
    return h.hexdigest()


def _resumo(nome: str, payload: Any) -> Dict[str, Any]:
    try:
        if nome == "intencoes.json":
            itens = payload.get("intencoes", [])
            return {"total": len(itens), "aprovadas": sum(1 for i in itens if i.get("status") == "aprovada")}
        if nome == "readiness.json":
            return {"prontas": sum(1 for a in payload.get("avaliadas", []) if a.get("pronto_para_R621"))}
        if nome == "minuta_r621.json":
            return {"minutas": payload.get("total")}
        if nome == "pareceres.json":
            return {"pareceres": payload.get("total")}
    except (AttributeError, TypeError):
        pass
    return {}


def emitir(piloto_dir: str, destino_dir: str) -> Dict[str, Any]:
    """Coleta 7 artefatos com hashes e escreve dossie_final.json."""
    os.makedirs(destino_dir, exist_ok=True)
    artefatos: List[Dict[str, Any]] = []
    for nome in ARTEFATOS:
        p = os.path.join(piloto_dir, nome)
        if not os.path.isfile(p):
            artefatos.append({"arquivo": nome, "ausente": True})
            continue
        try:
            with open(p, encoding="utf-8") as fh:
                txt = fh.read()
            try:
                payload = json.loads(txt)
            except ValueError:
                payload = {"linhas": len(txt.splitlines())}
            artefatos.append({"arquivo": nome, "ausente": False, "bytes": os.path.getsize(p),
                              "sha256": _sha(p), "resumo": _resumo(nome, payload)})
        except OSError as exc:
            artefatos.append({"arquivo": nome, "ausente": True, "erro": type(exc).__name__})
    payload = {"spec_id": SPEC_ID, "gerador": GERADOR,
               "gerado_em": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "cadeia": SPECS, "artefatos": artefatos,
               "pendencias_titular": ["ratificar piloto 3+1", "decidir 12 restantes",
                                      "re-pin sympy ou aceitar divergência", "revisão jurídica AI-Scientist"],
               "ratificacao_titular_pendente": True, "rotulo": "candidato_a_inspecao",
               "nota": "Dossiê para leitura única; nada decidido ou federado."}
    alvo = os.path.join(destino_dir, "dossie_final.json")
    with open(alvo, "w", encoding="utf-8") as fh:
        json.dump(copy.deepcopy(payload), fh, ensure_ascii=False, indent=2)
    return {"ok": True, "arquivo": alvo, "artefatos": len(artefatos)}
