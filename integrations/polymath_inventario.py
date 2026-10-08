# -*- coding: utf-8 -*-
"""Inventário autônomo 100% local (SPEC-935-R720).

Lê clones e readiness; nunca rede, subprocesso, decisão ou federação.
"""
from __future__ import annotations

import copy
import datetime
import hashlib
import json
import os
from typing import Any, Dict, List

SPEC_ID = "SPEC-935-R720"
GERADOR = "marceloclaro"
_MAX_ARQ = 5000
_MAX_HASH_BYTES = 500 * 1024
_IGNORAR = {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv"}

MARCOS = ["README.md", "README.rst", "LICENSE", "LICENSE.txt", "LICENSE.md",
          "pyproject.toml", "setup.py", "setup.cfg", "CITATION.cff"]


def _sha(path: str) -> str | None:
    try:
        if os.path.getsize(path) > _MAX_HASH_BYTES:
            return None
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for b in iter(lambda: fh.read(65536), b""):
                h.update(b)
        return h.hexdigest()
    except OSError:
        return None


def inventariar(clone_path: str) -> Dict[str, Any]:
    """Inventaria arquivos, marcos e HEAD sem seguir links."""
    arquivos: List[Dict[str, Any]] = []
    for raiz, dirs, nomes in os.walk(clone_path, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in _IGNORAR and not os.path.islink(os.path.join(raiz, d)))
        for n in sorted(nomes):
            p = os.path.join(raiz, n)
            if os.path.islink(p):
                continue
            rel = os.path.relpath(p, clone_path)
            if rel.startswith(".git" + os.sep) or rel == ".git":
                continue
            try:
                sz = os.path.getsize(p)
            except OSError:
                continue
            arquivos.append({"path": rel, "bytes": sz})
            if len(arquivos) >= _MAX_ARQ:
                break
        if len(arquivos) >= _MAX_ARQ:
            break
    total_bytes = sum(a["bytes"] for a in arquivos)
    ext: Dict[str, int] = {}
    for a in arquivos:
        _, ponto, sufixo = a["path"].rpartition(".")
        ext[("." + sufixo.lower()) if ponto else "(sem ext)"] = ext.get(("." + sufixo.lower()) if ponto else "(sem ext)", 0) + 1
    top10 = sorted(arquivos, key=lambda a: a["bytes"], reverse=True)[:10]
    marcos = {}
    for m in MARCOS:
        p = os.path.join(clone_path, m)
        ok = os.path.isfile(p)
        marcos[m] = {"presente": ok, "bytes": os.path.getsize(p) if ok else 0,
                     "sha256": _sha(p) if ok else None}
    for d in ("tests", "test", "docs", "examples"):
        p = os.path.join(clone_path, d)
        marcos[d + "/"] = {"presente": os.path.isdir(p)}
    head = None
    try:
        with open(os.path.join(clone_path, ".git", "HEAD"), encoding="utf-8") as fh:
            head = fh.read().strip() or None
    except OSError:
        head = None
    return {"total_arquivos": len(arquivos), "total_bytes": total_bytes, "top10": top10,
            "extensoes": ext, "marcos": marcos, "head": head}


def sha_conteudo(payload: Dict[str, Any]) -> str:
    """Hash determinístico excluindo gerado_em."""
    copia = {k: v for k, v in payload.items() if k != "gerado_em"}
    return hashlib.sha256(json.dumps(copia, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def relatorio(intencoes_dir: str, clones_base: str, destino_dir: str) -> Dict[str, Any]:
    """Gera relatório só dos prontos do readiness."""
    with open(os.path.join(intencoes_dir, "readiness.json"), encoding="utf-8") as fh:
        readiness = json.load(fh)
    prontos = [a for a in readiness.get("avaliadas", []) if a.get("pronto_para_R621")]
    os.makedirs(destino_dir, exist_ok=True)
    itens = []
    for a in prontos:
        url = str(a["url"])
        partes = url.rstrip("/").split("/")
        cand = os.path.join(clones_base, f"{partes[-2].lower()}__{partes[-1].lower()}")
        if not os.path.isdir(cand):
            cand = os.path.join(clones_base, partes[-1].lower())
        inv = inventariar(cand) if os.path.isdir(cand) else {"erro": "clone ausente"}
        itens.append({"url": url, "classe": a.get("classe"), "pronto_para_analise_R621": True,
                      "inventario": inv, "rotulo": "candidato_a_inspecao"})
    nao = [a for a in readiness.get("avaliadas", []) if not a.get("pronto_para_R621")]
    payload = {"spec_id": SPEC_ID, "gerador": GERADOR,
               "gerado_em": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "prontas": len(itens), "nao_prontos": len(nao), "itens": itens,
               "nao_prontos_detalhe": [{"url": a.get("url"), "pendencias": a.get("pendencias", [])} for a in nao],
               "rotulo": "candidato_a_inspecao", "exige_validacao_externa": True,
               "nota": "Inventário para análise R621; nada federado."}
    payload["sha256_relatorio"] = sha_conteudo(payload)
    with open(os.path.join(destino_dir, "relatorio_autonomo.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    return {"ok": True, "destino": destino_dir, "prontas": len(itens)}
