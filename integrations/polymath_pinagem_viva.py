# -*- coding: utf-8 -*-
"""Executor vivo da pinagem polímata (SPEC-935-R714).

Somente com consentimento=true explícito. Token lido de env GITHUB_TOKEN ou
parâmetro, nunca persistido nem logado. Sem clonar/executar terceiros.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import urllib.request
from typing import Any, Callable, Dict

from integrations.github_polymath_labs import validar_url
from integrations import polymath_pinagem as nucleo

SPEC_ID = "SPEC-935-R714"
GERADOR = "marceloclaro"

_UA = "opencode-polymath/1.0"


def fetcher_vivo(org: str, repo: str, token: str | None = None, timeout: int = 20) -> Dict[str, Any]:
    """Busca metadados vivos após validar allowlist. Falha vira exceção."""
    validar_url(f"https://github.com/{org}/{repo}")
    url_api = f"https://api.github.com/repos/{org}/{repo}"
    headers = {"User-Agent": _UA, "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url_api, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        dados = json.loads(resp.read().decode("utf-8", "ignore"))
    lic = dados.get("license") or {}
    spdx = lic.get("spdx_id") or lic.get("key") or lic.get("name")
    license_ok = bool(spdx) and str(spdx).upper() not in ("NOASSERTION", "NONE", "OTHER")
    proc = subprocess.run(
        ["git", "ls-remote", f"https://github.com/{org}/{repo}", "HEAD"],
        capture_output=True, text=True, timeout=timeout,
    )
    if proc.returncode != 0:
        raise ConnectionError(f"ls-remote falhou para {org}/{repo}.")
    m = re.search(r"\b([0-9a-f]{40})\b", proc.stdout or "", re.IGNORECASE)
    if not m:
        raise ValueError(f"HEAD ilegível para {org}/{repo}.")
    return {
        "commit": m.group(1).lower(),
        "pushed_at": dados.get("pushed_at", ""),
        "license": spdx,
        "license_ok": license_ok,
        "archived": bool(dados.get("archived")),
    }


def _fetcher_seco(org: str, repo: str) -> Dict[str, Any]:
    agora = datetime.datetime.now(datetime.timezone.utc)
    base = int.from_bytes(f"{org}/{repo}".encode(), "little") % 30
    dt = (agora - datetime.timedelta(days=base)).isoformat()
    return {"commit": "0" * 40, "pushed_at": dt, "license": "MIT", "license_ok": True, "archived": False}


def executar(destino_dir: str, consentimento: bool, dias: int = 90,
             token: str | None = None, fetcher: Callable | None = None,
             consentido_por: str = "operador") -> Dict[str, Any]:
    """Executa revalidação + emissão + vivo_meta. Fail-closed sem True literal."""
    if consentimento is not True:
        raise ValueError("Execução viva exige consentimento=true explícito (R714).")
    if not isinstance(destino_dir, str) or not destino_dir.strip():
        raise ValueError("destino_dir vazio (fail-closed).")
    real_fetcher = fetcher if fetcher is not None else (lambda o, r: fetcher_vivo(o, r, token=token))
    resultado = nucleo.revalidar_todos(real_fetcher, dias=dias)
    recibo = nucleo.emitir_pins(destino_dir, resultado)
    meta = {"spec_id": SPEC_ID, "gerador": GERADOR, "gerado_em": resultado["gerado_em"],
            "consentimento": True, "consentido_por": consentido_por,
            "token_presente": bool(token), "janela_dias": dias,
            "total": resultado["total"], "federaveis": resultado["federaveis"],
            "nota": "Rotina viva auditada; decisão humana exigida. Nenhum lab atestado como final."}
    with open(os.path.join(destino_dir, "vivo_meta.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=2)
    return {"ok": True, **recibo, "federaveis": resultado["federaveis"]}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Pinagem viva polímata (R714).")
    ap.add_argument("--dest", required=True)
    ap.add_argument("--consentimento", required=True, help="Use literalmente 'true'.")
    ap.add_argument("--dias", type=int, default=90)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--fresco-apenas", action="store_true")
    ns = ap.parse_args(argv)
    if ns.consentimento != "true":
        print("Recusado: --consentimento deve ser literalmente 'true' (R714).", file=sys.stderr)
        return 2
    token = os.environ.get("GITHUB_TOKEN")
    fetcher = _fetcher_seco if ns.dry_run else None
    try:
        out = executar(ns.dest, consentimento=True, dias=ns.dias, token=token, fetcher=fetcher)
    except Exception as exc:
        print(f"Falha: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    if ns.fresco_apenas:
        print(f"Federáveis: {out['federaveis']}/{out['total']} em {ns.dest}")
    else:
        print(f"OK: {out['total']} pins em {ns.dest} (federáveis {out['federaveis']}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
