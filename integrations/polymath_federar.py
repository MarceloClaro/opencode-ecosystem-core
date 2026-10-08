# -*- coding: utf-8 -*-
"""Decisão, rede e federação no escopo polímata (SPEC-935-R724).

Titular decide com humano True + ordem explícita. Rede e federados vivem em
workbench/rede_polimata, nunca no harness R621. Sem instalar/executar.
"""
from __future__ import annotations

import copy
import datetime
import json
import os
from typing import Any, Dict, List

from integrations import polymath_intencoes as inten

SPEC_ID = "SPEC-935-R724"
GERADOR = "marceloclaro"
ALVOS = ["https://github.com/pgmpy/pgmpy", "https://github.com/proportione/prisma"]


def _ler_json(path: str) -> Any:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def decidir_titular(intencoes_dir: str, humano: bool, ordem: str, responsavel: str,
                    motivos: Dict[str, str]) -> Dict[str, Any]:
    """Aprova só alvos com minuta+parecer+readiness pronto. Ordem deve conter decida+federe."""
    if humano is not True:
        raise ValueError("Decisão titular exige humano=true (R724).")
    if not isinstance(ordem, str) or ("decida" not in ordem.lower() or "federe" not in ordem.lower()):
        raise ValueError("Ordem deve conter 'decida' e 'federe' (R724).")
    if not isinstance(responsavel, str) or not responsavel.strip():
        raise ValueError("responsavel vazio (fail-closed).")
    minuta = {m["artifact_id"]: m for m in _ler_json(os.path.join(intencoes_dir, "minuta_r621.json")).get("minutas", [])}
    parecer = {p["url"].lower(): p for p in _ler_json(os.path.join(intencoes_dir, "pareceres.json")).get("pareceres", [])}
    readiness = {a["url"].lower(): a for a in _ler_json(os.path.join(intencoes_dir, "readiness.json")).get("avaliadas", [])}
    por_url = {u.lower(): u for u in ALVOS}
    aprovadas = []
    for url_l, url in por_url.items():
        if url_l not in [k.lower() for k in motivos.keys()]:
            continue
        mot = motivos.get(url, "") or motivos.get(url_l, "")
        if not isinstance(mot, str) or not mot.strip():
            raise ValueError(f"Motivo vazio para {url}.")
        # exige tríade
        if not any(url_l in str(m.get("artifact_id", "")).lower() or True for m in minuta.values()):
            pass
        tem_minuta = any(url_l.split("/")[-1] in m.get("artifact_id", "") for m in minuta.values())
        if not tem_minuta:
            raise ValueError(f"Sem minuta para {url}.")
        if url_l not in parecer:
            raise ValueError(f"Sem parecer para {url}.")
        rd = readiness.get(url_l)
        if rd is None or not rd.get("pronto_para_R621"):
            raise ValueError(f"Sem readiness pronto para {url}.")
        r = inten.decidir(intencoes_dir, url, "aprovada", humano=True, motivo=mot, responsavel=responsavel)
        aprovadas.append(r["url"])
    return {"ok": True, "aprovadas": len(aprovadas), "urls": aprovadas}


def adicionar_rede(intencoes_dir: str, rede_dir: str) -> Dict[str, Any]:
    """Registra nodos roteáveis só de aprovadas com minuta+parecer."""
    payload = _ler_json(os.path.join(intencoes_dir, "intencoes.json"))
    minuta = _ler_json(os.path.join(intencoes_dir, "minuta_r621.json")).get("minutas", [])
    por_minuta: Dict[str, Any] = {}
    for m in minuta:
        u = str(m.get("url", "") or "").lower()
        if u:
            por_minuta[u] = m
            continue
        for u2 in ALVOS:  # compat: minutas R721 sem campo url
            if u2.split("/")[-1].lower() in str(m.get("artifact_id", "")):
                por_minuta[u2.lower()] = m
    os.makedirs(rede_dir, exist_ok=True)
    nodos = []
    for it in payload.get("intencoes", []):
        if it.get("status") != "aprovada":
            continue
        url_l = str(it.get("url", "")).lower()
        m = por_minuta.get(url_l)
        if m is None:
            continue
        slug = str(m["artifact_id"]).split(":")[-1]
        nodos.append({
            "agent_id": f"polymath:lab:{slug}", "artifact_id": m["artifact_id"],
            "url": it["url"], "classe": it.get("classe"),
            "capabilities": ["raciocinio-cientifico", slug],
            "status": "available", "confidence_score": 0.6, "load": 0.0,
            "license": m.get("license", ""), "source_path": m.get("source_path", ""),
            "execution_verified": False, "instruction_only": True,
        })
    with open(os.path.join(rede_dir, "nodos.json"), "w", encoding="utf-8") as fh:
        json.dump({"spec_id": SPEC_ID, "gerador": GERADOR,
                   "gerado_em": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   "total": len(nodos), "nodos": nodos,
                   "rotulo": "candidato_federado_exige_supervisao"}, fh, ensure_ascii=False, indent=2)
    return {"ok": True, "nodos": len(nodos), "rede": rede_dir}


def federar(rede_dir: str, intencoes_dir: str) -> Dict[str, Any]:
    """Federa escopo polímata com cadeia de hashes. Nada em harness."""
    nodos = _ler_json(os.path.join(rede_dir, "nodos.json")).get("nodos", [])
    cadeia_docs = {}
    for nome in ("intencoes.json", "minuta_r621.json", "pareceres.json", "readiness.json",
                 "relatorio_autonomo.json", "decisoes_humanas.jsonl"):
        p = os.path.join(intencoes_dir, nome)
        if os.path.isfile(p):
            import hashlib
            h = hashlib.sha256()
            with open(p, "rb") as fh:
                for b in iter(lambda: fh.read(65536), b""):
                    h.update(b)
            cadeia_docs[nome] = {"bytes": os.path.getsize(p), "sha256": h.hexdigest()}
    federados = []
    for n in nodos:
        federados.append({**copy.deepcopy(n), "federado_no_escopo_polimata": True,
                          "escopo": "polimata", "quando": datetime.datetime.now(datetime.timezone.utc).isoformat()})
    payload = {"spec_id": SPEC_ID, "gerador": GERADOR,
               "gerado_em": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "escopo": "polimata", "total": len(federados), "federados": federados,
               "cadeia": cadeia_docs, "rotulo": "candidato_federado_exige_supervisao",
               "nota": "Federado no escopo polímata; não é federação harness R621."}
    alvo = os.path.join(rede_dir, "federados.json")
    with open(alvo, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    return {"ok": True, "arquivo": alvo, "federados": len(federados)}
