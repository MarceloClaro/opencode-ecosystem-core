# -*- coding: utf-8 -*-
"""Federação por classe com licença confirmada (SPEC-935-R715).

Sem rede, sem auto-federação. Decide proposto|retido para decisão humana.
"""
from __future__ import annotations

import copy
import datetime
import json
import os
import re
from typing import Any, Dict, List

from integrations.github_polymath_labs import ALLOWLIST

SPEC_ID = "SPEC-935-R715"
GERADOR = "marceloclaro"

CLASSES: Dict[str, Dict[str, Any]] = {
    "ativo": {"dias": 90, "urls": [
        "https://github.com/internscience/scireason", "https://github.com/idiap/scir",
        "https://github.com/irving-feng/cot-evo", "https://github.com/kmineshima/abduction-syllogism-llm",
        "https://github.com/aswinesag/research-reasoning-engine", "https://github.com/pgmpy/pgmpy",
        "https://github.com/py-why/dowhy", "https://github.com/pymc-labs/causalpy",
        "https://github.com/mckinsey/causalnex"]},
    "formal-estavel": {"dias": 730, "urls": [
        "https://github.com/z3prover/z3", "https://github.com/sympy/sympy",
        "https://github.com/reasonkit/reasonkit-core"]},
    "sintese-referencia": {"dias": 730, "urls": [
        "https://github.com/proportione/prisma", "https://github.com/cqh4046/prisma-traice",
        "https://github.com/ohdsi/evidencesynthesis", "https://github.com/aweai-team/aiscientist",
        "https://github.com/sakanaai/ai-scientist"]},
    "laboratorio-estavel": {"dias": 1095, "urls": [
        "https://github.com/samuelschmidgall/agentlaboratory", "https://github.com/rasilab/github_demo",
        "https://github.com/rasilab/github_template", "https://github.com/aqibrahimbt/repro_audit"]},
}

_URL_CLASSE = {u.lower(): c for c, v in CLASSES.items() for u in v["urls"]}
_HEX40 = re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE)


def classificar(url: str) -> str:
    """Mapeia URL da allowlist à classe. Fora levanta ValueError sem rede."""
    if not isinstance(url, str) or not url.strip():
        raise ValueError("URL vazia (fail-closed).")
    chave = url.strip().rstrip("/").lower()
    if chave.endswith(".git"):
        chave = chave[:-4]
    if chave not in _URL_CLASSE:
        raise ValueError(f"Fora da allowlist R711: {url!r}.")
    return _URL_CLASSE[chave]


def janela_da_classe(classe: str) -> int:
    return int(CLASSES[classe]["dias"])


def propor(pins: List[Dict[str, Any]], overrides: Dict[str, Dict[str, str]],
           dias_por_classe: Dict[str, int] | None = None) -> Dict[str, Any]:
    """Aplica janela da classe + override de licença. Tolerante a pin ausente."""
    if not isinstance(pins, list):
        raise ValueError("pins deve ser lista.")
    if not isinstance(overrides, dict):
        raise ValueError("overrides deve ser objeto.")
    janelas = {c: int(v["dias"]) for c, v in CLASSES.items()}
    if dias_por_classe:
        for c, d in dias_por_classe.items():
            if c in janelas:
                janelas[c] = int(d)
    norm_over = {str(k).lower(): v for k, v in overrides.items()}
    decisoes = []
    for p in pins:
        url = str(p.get("url", ""))
        try:
            classe = classificar(url)
        except ValueError as exc:
            decisoes.append({"url": url, "classe": None, "decisao": "retido", "motivo": str(exc)})
            continue
        janela = janelas[classe]
        commit = str(p.get("commit") or "")
        idade = p.get("idade_dias")
        arquivado = bool(p.get("archived"))
        ok_viva = bool(p.get("license_ok"))
        ov = norm_over.get(url.lower())
        ov_ok = isinstance(ov, dict) and all(
            isinstance(ov.get(k), str) and ov.get(k).strip()
            for k in ("licenca", "url_license", "sha256_license", "confirmado_por"))
        if ov_ok and len(ov["sha256_license"]) != 64:
            ov_ok = False
        licenca_final = (ov["licenca"] if ov_ok else p.get("license"))
        if not commit or not _HEX40.match(commit):
            decisoes.append({"url": url, "classe": classe, "decisao": "retido", "motivo": "commit ausente ou inválido."})
        elif arquivado:
            decisoes.append({"url": url, "classe": classe, "decisao": "retido", "motivo": "arquivado."})
        elif not (ok_viva or ov_ok):
            dec = {"url": url, "classe": classe, "decisao": "retido",
                   "motivo": "licença viva não confirmada e sem override auditado."}
            if ov is not None and not ov_ok:
                dec["motivo"] = "override incompleto (exige licenca+url_license+sha256+confirmado_por)."
            decisoes.append(dec)
        elif not isinstance(idade, int) or idade < 0:
            decisoes.append({"url": url, "classe": classe, "decisao": "retido", "motivo": "idade_dias ilegível."})
        elif idade > janela:
            decisoes.append({"url": url, "classe": classe, "decisao": "retido",
                             "motivo": f"desatualizado na classe {classe}: {idade}d > {janela}d."})
        else:
            motivo = f"dentro da janela {classe} ({idade}d ≤ {janela}d)"
            if ov_ok and not ok_viva:
                motivo += f"; licença {licenca_final} via override {ov['url_license']}"
            decisoes.append({"url": url, "classe": classe, "decisao": "proposto",
                             "motivo": motivo, "licenca": licenca_final})
    propostos = sum(1 for d in decisoes if d["decisao"] == "proposto")
    return {"spec_id": SPEC_ID, "gerador": GERADOR,
            "gerado_em": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "classes": {c: {"dias": janelas[c]} for c in CLASSES},
            "total": len(decisoes), "propostos": propostos, "retidos": len(decisoes) - propostos,
            "decisoes": decisoes, "rotulo": "candidato_a_inspecao", "exige_validacao_externa": True,
            "nota": "Proposta para decisão humana; nada federado automaticamente."}


def emitir_proposta(destino_dir: str, proposta: Dict[str, Any]) -> Dict[str, Any]:
    """Escreve federacao_proposta.json."""
    if not isinstance(destino_dir, str) or not destino_dir.strip():
        raise ValueError("destino_dir vazio (fail-closed).")
    if not isinstance(proposta, dict) or "decisoes" not in proposta:
        raise ValueError("proposta inválida.")
    os.makedirs(destino_dir, exist_ok=True)
    alvo = os.path.join(destino_dir, "federacao_proposta.json")
    with open(alvo, "w", encoding="utf-8") as fh:
        json.dump(copy.deepcopy(proposta), fh, ensure_ascii=False, indent=2)
    return {"ok": True, "arquivo": alvo, "total": proposta.get("total", 0)}
