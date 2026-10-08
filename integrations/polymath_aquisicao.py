# -*- coding: utf-8 -*-
"""Aquisição auditada sem executar (SPEC-935-R719).

Clone --depth 1 confinado, somente com consentimento True literal, allowlist e
intenção aprovada. Registra HEAD+hash em aquisicoes.jsonl. Sem build/install.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import subprocess
from typing import Any, Dict

from integrations.github_polymath_labs import validar_url

SPEC_ID = "SPEC-935-R719"
GERADOR = "marceloclaro"


def _aprovada(intencoes_dir: str, url: str) -> bool:
    try:
        with open(os.path.join(intencoes_dir, "intencoes.json"), encoding="utf-8") as fh:
            itens = json.load(fh).get("intencoes", [])
    except (OSError, ValueError):
        return False
    return any(str(i.get("url", "")).lower() == url.lower() and i.get("status") == "aprovada" for i in itens)


def clonar_auditado(url: str, base_destino: str, consentimento: bool, intencoes_dir: str,
                    timeout: int = 120) -> Dict[str, Any]:
    """Clona shallow com trilha. Fail-closed antes de subprocesso."""
    if consentimento is not True:
        raise ValueError("Aquisição exige consentimento=true explícito (R719).")
    canonica = validar_url(url)
    if not isinstance(base_destino, str) or not base_destino.strip():
        raise ValueError("base_destino vazio (fail-closed).")
    if not _aprovada(intencoes_dir, canonica):
        raise ValueError(f"Sem intenção aprovada para {url!r}; aquisição recusada.")
    partes = canonica[len("https://github.com/"):].split("/")
    destino = os.path.join(base_destino, f"{partes[0].lower()}__{partes[1].lower()}")
    os.makedirs(base_destino, exist_ok=True)
    if os.path.isdir(os.path.join(destino, ".git")):
        head_path = os.path.join(destino, ".git", "HEAD")
        try:
            with open(head_path, encoding="utf-8") as fh:
                head = fh.read().strip()
        except OSError:
            head = ""
        return {"adquirido": True, "reutilizado": True, "destino": destino,
                "head_legivel": bool(head), "sha256_head": hashlib.sha256(head.encode()).hexdigest() if head else None}
    proc = subprocess.run(["git", "clone", "--depth", "1", canonica, destino],
                          capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        raise ValueError(f"git clone falhou para {canonica}: {(proc.stderr or '')[:200]}")
    try:
        with open(os.path.join(destino, ".git", "HEAD"), encoding="utf-8") as fh:
            head = fh.read().strip()
    except OSError:
        head = ""
    registro = {"quando": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "url": canonica, "destino": destino, "head": head,
                "sha256_head": hashlib.sha256(head.encode()).hexdigest() if head else None,
                "adquirido": True, "nota": "Adquirido, não verificado; sem build ou execução."}
    with open(os.path.join(base_destino, "aquisicoes.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(registro, ensure_ascii=False) + "\n")
    return {"adquirido": True, "reutilizado": False, "destino": destino,
            "head_legivel": bool(head), "sha256_head": registro["sha256_head"]}
