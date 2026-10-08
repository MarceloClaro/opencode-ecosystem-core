# -*- coding: utf-8 -*-
"""Pinagem viva e gate de federação polímata (SPEC-935-R713).

Rotina operacional com fetcher injetável. O gate hermético usa fetcher falso;
a rotina viva (rede/subprocesso) exige consentimento explícito do operador e
vive fora dos testes, documentada em `rotina_viva_exemplo()`.

Orquestração ao orquestrador; este módulo é ferramenta auditável, sem executar
terceiros e sem autoridade epistêmica.
"""
from __future__ import annotations

import copy
import datetime
import hashlib
import json
import os
import re
from typing import Any, Callable, Dict

from integrations.github_polymath_labs import ALLOWLIST, validar_url

SPEC_ID = "SPEC-935-R713"
GERADOR = "marceloclaro"
JANELA_DIAS = 90

_HEX40 = re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE)


def _agora_utc() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def _parse_iso(s: Any) -> datetime.datetime | None:
    if not isinstance(s, str) or not s.strip():
        return None
    try:
        iso = s.strip().replace("Z", "+00:00")
        dt = datetime.datetime.fromisoformat(iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    except ValueError:
        return None


def _sha_registro(nucleo: Dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(nucleo, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def pinar_lab(url: str, fetcher: Callable[[str, str], Dict[str, Any]], dias: int = JANELA_DIAS) -> Dict[str, Any]:
    """Pina um lab da allowlist via fetcher(org, repo). Fail-closed antes da rede."""
    canonica = validar_url(url)  # levanta ValueError fora da allowlist; sem rede
    partes = canonica[len("https://github.com/"):].split("/")
    org, repo = partes[0], partes[1]
    bruto = fetcher(org, repo)
    if not isinstance(bruto, dict):
        raise ValueError("fetcher deve retornar objeto.")
    commit = str(bruto.get("commit", "") or "").lower()
    pushed_at = bruto.get("pushed_at", "")
    licenca = bruto.get("license")
    license_ok = bool(bruto.get("license_ok"))
    arquivado = bool(bruto.get("archived"))
    dt = _parse_iso(pushed_at)
    agora = _agora_utc()
    idade_dias = (agora - dt).days if dt else None
    federavel = True
    motivo = "ok"
    if not _HEX40.match(commit):
        federavel, motivo = False, "commit ausente ou inválido (esperado 40 hex)."
    elif arquivado:
        federavel, motivo = False, "repositório arquivado."
    elif not license_ok:
        federavel, motivo = False, "licença viva não confirmada (license_undeclared bloqueia federação)."
    elif dt is None:
        federavel, motivo = False, "pushed_at ilegível; manutenção não verificável."
    elif idade_dias is not None and idade_dias > dias:
        federavel, motivo = False, f"desatualizado: {idade_dias}d desde push, janela {dias}d."
    elif idade_dias is not None and idade_dias < 0:
        federavel, motivo = False, "pushed_at no futuro; relógio ou dado inválido."
    if federavel:
        motivo = "ok"
    nucleo = {"url": canonica, "commit": commit, "pushed_at": pushed_at, "license": licenca, "archived": arquivado}
    return {
        "url": canonica, "org": org, "repo": repo, "commit": commit or None,
        "pushed_at": pushed_at or None, "idade_dias": idade_dias,
        "license": licenca, "license_ok": license_ok, "archived": arquivado,
        "federavel": federavel, "motivo": motivo,
        "auditado_em": agora.isoformat(), "sha256_registro": _sha_registro(nucleo),
    }


def revalidar_todos(fetcher: Callable[[str, str], Dict[str, Any]], dias: int = JANELA_DIAS) -> Dict[str, Any]:
    """Percorre allowlist; falha isolada vira bloqueado sem abortar."""
    pins = []
    for lab in ALLOWLIST:
        try:
            pins.append(pinar_lab(lab["url"], fetcher, dias=dias))
        except ValueError as exc:
            pins.append({"url": lab["url"], "org": "", "repo": "", "commit": None, "federavel": False,
                         "motivo": f"fail-closed local: {exc}", "auditado_em": _agora_utc().isoformat(),
                         "sha256_registro": _sha_registro({"url": lab["url"]})})
        except Exception as exc:
            pins.append({"url": lab["url"], "org": "", "repo": "", "commit": None, "federavel": False,
                         "motivo": f"fetcher falhou: {type(exc).__name__}", "auditado_em": _agora_utc().isoformat(),
                         "sha256_registro": _sha_registro({"url": lab["url"]})})
    fed = sum(1 for p in pins if p.get("federavel"))
    return {"spec_id": SPEC_ID, "gerador": GERADOR, "gerado_em": _agora_utc().isoformat(),
            "janela_dias": dias, "total": len(pins), "federaveis": fed,
            "bloqueados": len(pins) - fed, "pins": pins}


def emitir_pins(destino_dir: str, resultado: Dict[str, Any]) -> Dict[str, Any]:
    """Escreve labs_pins.json + federacao_gate.json reproduzíveis."""
    if not isinstance(destino_dir, str) or not destino_dir.strip():
        raise ValueError("destino_dir vazio (fail-closed).")
    if not isinstance(resultado, dict) or "pins" not in resultado:
        raise ValueError("resultado inválido (esperado revalidar_todos).")
    os.makedirs(destino_dir, exist_ok=True)
    pins = copy.deepcopy(resultado["pins"])
    base = {"spec_id": SPEC_ID, "gerador": GERADOR, "gerado_em": resultado.get("gerado_em"),
            "janela_dias": resultado.get("janela_dias", JANELA_DIAS),
            "total": resultado.get("total", len(pins)), "pins": pins}
    gate = {"spec_id": SPEC_ID, "gerador": GERADOR, "gerado_em": base["gerado_em"],
            "janela_dias": base["janela_dias"], "total": base["total"],
            "federaveis": resultado.get("federaveis", 0), "bloqueados": resultado.get("bloqueados", 0),
            "decisoes": [{"url": p["url"], "federavel": bool(p.get("federavel")), "motivo": p.get("motivo", "")} for p in pins],
            "nota": "Gate de federação; decisão humana exigida. Nenhum lab atestado como final."}
    for nome, payload in (("labs_pins.json", base), ("federacao_gate.json", gate)):
        with open(os.path.join(destino_dir, nome), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
    return {"ok": True, "destino": destino_dir, "total": len(pins)}


def rotina_viva_exemplo() -> Dict[str, Any]:
    """Documenta rotina viva fora do gate; não executa rede."""
    return {
        "passos": [
            "1) Operador autoriza rede explicitamente (consentimento=true).",
            "2) Para cada org/repo: GET https://api.github.com/repos/<org>/<repo> (pushed_at, license, archived).",
            "3) HEAD via git ls-remote https://github.com/<org>/<repo> HEAD.",
            "4) Chamar revalidar_todos(fetcher_vivo) e emitir_pins().",
            "5) Decisão humana de federação sobre federacao_gate.json.",
        ],
        "proibido_no_gate": ["requests", "urlopen", "subprocess"],
        "nota": "Exemplo inerte; execução pertence ao operador.",
    }
