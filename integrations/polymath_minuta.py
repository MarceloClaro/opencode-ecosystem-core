# -*- coding: utf-8 -*-
"""Minuta R621 sem federar (SPEC-935-R721).

Lê relatório autônomo + clones; propõe artefatos polymath:spec:third_party.
Sem rede, subprocesso, decisão ou escrita em harness.
"""
from __future__ import annotations

import copy
import datetime
import hashlib
import json
import os
import re
from typing import Any, Dict

SPEC_ID = "SPEC-935-R721"
GERADOR = "marceloclaro"
_SLUG = re.compile(r"[^a-z0-9]+")


def _slug(url: str) -> str:
    partes = url.rstrip("/").split("/")
    base = f"{partes[-2]}-{partes[-1]}".lower()
    return _SLUG.sub("-", base).strip("-")


def _descricao(readme_path: str | None, fallback: str) -> str:
    if readme_path and os.path.isfile(readme_path):
        try:
            with open(readme_path, encoding="utf-8", errors="ignore") as fh:
                linhas = [l.strip() for l in fh.read().splitlines() if l.strip().lstrip("# ").strip()][:3]
            texto = " ".join(linhas)[:240].strip()
            if texto:
                return texto
        except OSError:
            pass
    return f"Fallback R711: {fallback}"


def emitir(intencoes_dir: str, clones_base: str, destino_dir: str, licencas: Dict[str, str],
           tipos: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Gera minuta_r621.json só dos prontos para análise."""
    with open(os.path.join(intencoes_dir, "relatorio_autonomo.json"), encoding="utf-8") as fh:
        rel = json.load(fh)
    os.makedirs(destino_dir, exist_ok=True)
    minutas = []
    norm_lic = {str(k).lower(): v for k, v in licencas.items()}
    for it in rel.get("itens", []):
        if not it.get("pronto_para_analise_R621"):
            continue
        url = str(it["url"])
        partes = url.rstrip("/").split("/")
        cand = os.path.join(clones_base, f"{partes[-2].lower()}__{partes[-1].lower()}")
        readme = os.path.join(cand, "README.md")
        if not os.path.isfile(readme):
            readme = None
        info = tipos.get(url, {})
        desc = _descricao(readme, str(info.get("uso", "lab curado R711")))
        sha = None
        if readme:
            h = hashlib.sha256()
            with open(readme, "rb") as fh:
                for b in iter(lambda: fh.read(65536), b""):
                    h.update(b)
            sha = h.hexdigest()
        else:
            sha = hashlib.sha256(desc.encode()).hexdigest()
        minutas.append({
            "artifact_id": f"polymath:spec:third_party:{_slug(url)}",
            "url": url,
            "ecosystem": "polymath", "kind": "spec", "origin": "third_party",
            "name": _slug(url), "description": desc,
            "source_path": readme or cand, "license": norm_lic.get(url.lower(), ""),
            "capabilities": list(info.get("tipo", [])),
            "content_sha256": sha, "proposta_para_federacao": True,
            "ratificacao_titular_pendente": True,
        })
    payload = {"spec_id": SPEC_ID, "gerador": GERADOR,
               "gerado_em": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "total": len(minutas), "minutas": minutas,
               "rotulo": "candidato_a_inspecao", "exige_validacao_externa": True,
               "nota": "Minuta para ratificação; nada federado."}
    alvo = os.path.join(destino_dir, "minuta_r621.json")
    with open(alvo, "w", encoding="utf-8") as fh:
        json.dump(copy.deepcopy(payload), fh, ensure_ascii=False, indent=2)
    return {"ok": True, "arquivo": alvo, "total": len(minutas)}
