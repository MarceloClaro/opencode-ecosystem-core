# -*- coding: utf-8 -*-
"""Readiness R621 do piloto (SPEC-935-R718).

Cruza intenção aprovada + pin + licença + clone local. Diagnostica, não federa.
Sem rede, sem subprocesso, sem escrita fora do diretório de intenções.
"""
from __future__ import annotations

import copy
import datetime
import json
import os
from typing import Any, Dict, List

SPEC_ID = "SPEC-935-R718"
GERADOR = "marceloclaro"


def avaliar(intencoes_dir: str, pins: List[Dict[str, Any]], clones_base: str,
            overrides: Dict[str, Dict[str, str]] | None = None,
            janelas: Dict[str, int] | None = None) -> Dict[str, Any]:
    """Avalia aprovadas; demais viram não avaliadas sem falhar."""
    with open(os.path.join(intencoes_dir, "intencoes.json"), encoding="utf-8") as fh:
        intencoes = json.load(fh).get("intencoes", [])
    por_pin = {str(p.get("url", "")).lower(): p for p in pins}
    norm_over = {str(k).lower(): v for k, v in (overrides or {}).items()}
    avaliadas = []
    for it in intencoes:
        url = str(it.get("url", ""))
        if it.get("status") != "aprovada":
            avaliadas.append({"url": url, "avaliado": False,
                              "motivo": f"status {it.get('status')}, somente aprovada é avaliada."})
            continue
        pend: List[str] = []
        pin = por_pin.get(url.lower())
        ov0 = norm_over.get(url.lower())
        ov_pin_ok = isinstance(ov0, dict) and all(isinstance(ov0.get(k), str) and ov0.get(k).strip() for k in ("licenca", "url_license", "sha256_license", "confirmado_por")) and len(ov0.get("sha256_license", "")) == 64
        pin_suprido = False
        if pin is None or not pin.get("federavel"):
            motivo_pin = str((pin or {}).get("motivo", "sem pin"))
            so_licenca = "licença" in motivo_pin.lower() or "license" in motivo_pin.lower()
            so_idade = "desatualizado" in motivo_pin.lower()
            commit_ok = bool(pin) and bool(pin.get("commit")) and not pin.get("archived")
            if ov_pin_ok and so_licenca and commit_ok:
                pin_suprido = True  # bloqueio só-licença suprido por override (regra R715)
            elif (janelas and so_idade and not so_licenca and commit_ok
                  and isinstance(pin.get("idade_dias"), int)
                  and pin["idade_dias"] <= int(janelas.get(url.lower(), 0))):
                pin_suprido = True  # bloqueio só-idade suprido pela janela da classe (R735)
                motivo_pin += " (suprido pela janela da classe)"
            if not pin_suprido:
                pend.append(f"pin ausente ou não federável: {motivo_pin}")
        if pin is not None and not (pin.get("license_ok")):
            ov = norm_over.get(url.lower())
            ov_ok = isinstance(ov, dict) and all(isinstance(ov.get(k), str) and ov.get(k).strip() for k in ("licenca", "url_license", "sha256_license", "confirmado_por")) and len(ov.get("sha256_license", "")) == 64
            if not ov_ok:
                pend.append("licença viva não confirmada no pin (exige override R715 auditado)")
        partes = url.rstrip("/").split("/")
        cand = [os.path.join(clones_base, f"{partes[-2].lower()}__{partes[-1].lower()}"),
                os.path.join(clones_base, partes[-1].lower())]
        achado = next((c for c in cand if os.path.isdir(c)), None)
        head_ok = False
        if achado is None:
            pend.append(f"clone ausente em {cand[0]} (operador deve clonar com consentimento)")
        else:
            try:
                with open(os.path.join(achado, ".git", "HEAD"), encoding="utf-8") as fh:
                    head_ok = bool(fh.read().strip())
                if not head_ok:
                    pend.append("HEAD ilegível no clone")
            except OSError:
                pend.append("HEAD ilegível no clone")
        avaliadas.append({"url": url, "avaliado": True, "classe": it.get("classe"),
                          "pronto_para_R621": not pend, "pendencias": pend,
                          "clone": achado, "head_legivel": head_ok})
    prontas = sum(1 for a in avaliadas if a.get("pronto_para_R621"))
    return {"spec_id": SPEC_ID, "gerador": GERADOR,
            "avaliado_em": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "total": len(avaliadas), "avaliadas": avaliadas, "prontas": prontas,
            "pendentes": len(avaliadas) - prontas,
            "rotulo": "candidato_a_inspecao"}


def emitir(intencoes_dir: str, relatorio: Dict[str, Any]) -> Dict[str, Any]:
    """Escreve readiness.json no diretório de intenções."""
    alvo = os.path.join(intencoes_dir, "readiness.json")
    with open(alvo, "w", encoding="utf-8") as fh:
        json.dump(copy.deepcopy(relatorio), fh, ensure_ascii=False, indent=2)
    return {"ok": True, "arquivo": alvo}
