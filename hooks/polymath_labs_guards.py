# -*- coding: utf-8 -*-
"""Guards fail-closed do pesquisador polímata (SPEC-935-R712).

Sem rede/subprocesso. Integra-se a `hooks/engine.py` via HookMatcher.
Orquestração permanece ao orquestrador; guards são ferramenta de bloqueio.
"""
from __future__ import annotations

import re
from typing import Any, Dict

try:
    from integrations.github_polymath_labs import validar_url
except ImportError:
    def validar_url(url: str) -> str:  # fallback fechado
        raise ValueError("Allowlist R711 indisponível.")

_CAUSAL_ABSOLUTO = re.compile(r"\b(causa|prov[ao]|eficaz|eficácia|cura|curas|comprovad[oa])\b", re.IGNORECASE)
_MITIGADOR = re.compile(r"\b(associad[oa]|correla|limita|suposi|hipótese|hipotese|preliminar|incert|intervalo|confian)\b", re.IGNORECASE)
_EXEC_TERCEIROS = re.compile(r"\b(pip\s+install|git\s+clone|docker\s+run|npm\s+(install|i)\s|curl\s.*\|\s*(ba)?sh)\b", re.IGNORECASE)


def guard_clone_url(url: Any) -> Dict[str, Any]:
    """Allow: apenas HTTPS GitHub da allowlist R711. Deny caso contrário."""
    if not isinstance(url, str) or not url.strip():
        return {"allow": False, "reason": "URL vazia rejeitada (fail-closed R712)."}
    u = url.strip()
    if u.startswith("git@") or u.startswith("http://"):
        return {"allow": False, "reason": f"Esquema não HTTPS: {url!r}."}
    try:
        validar_url(u)
        return {"allow": True, "reason": ""}
    except ValueError as exc:
        return {"allow": False, "reason": str(exc)}


def guard_claim(text: Any) -> Dict[str, Any]:
    """Deny em causal absoluto sem mitigador próximo; allow calibrado."""
    if not isinstance(text, str) or not text.strip():
        return {"allow": False, "reason": "Texto vazio não auditável (fail-closed)."}
    if _CAUSAL_ABSOLUTO.search(text) and not _MITIGADOR.search(text):
        return {"allow": False, "reason": "Alegação causal/absoluta sem mitigador (associado/limitação/suposição). Sem desenho, sem frase causal (R710/R712)."}
    return {"allow": True, "reason": ""}


def guard_third_party_exec(command: Any) -> Dict[str, Any]:
    """Deny em instalação/execução típica de terceiros; allow em leitura/listagem."""
    if not isinstance(command, str) or not command.strip():
        return {"allow": False, "reason": "Comando vazio rejeitado (fail-closed)."}
    if _EXEC_TERCEIROS.search(command):
        return {"allow": False, "reason": "Execução/instalação de terceiros exige consentimento explícito do operador (R712 fora de escopo)."}
    return {"allow": True, "reason": ""}
