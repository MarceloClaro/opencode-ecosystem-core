# -*- coding: utf-8 -*-
"""
Política padrão de hooks do Core (SPEC-935-R653) — deny-list + auditoria.

Deny-list documentada e testada para Bash destrutivo/exfiltrador. Todo o
resto passa: allowlist total paralisaria o agente; a deny-list é auditável
e evolui por adição (cada item tem teste).
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List

from .engine import HookMatcher

_AUDIT_DEFAULT = os.path.expanduser("~/.cache/opencode-hooks/audit.jsonl")

# (nome, regex) — ordem = ordem de avaliação; cada uma tem teste dedicado.
_DENY_PATTERNS: List[tuple] = [
    ("rm-rf-raiz", r"\brm\s+(-[a-z]*r[a-z]*f\s+|--recursive\s+--force\s+)(/|~|\$HOME|/\*)"),
    ("mkfs", r"\bmkfs(\.|$|\s)"),
    ("fork-bomb", r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;"),
    ("pipe-para-shell", r"\b(curl|wget)\b[^|]*\|\s*(sudo\s+)?(ba)?sh\b"),
    ("escrita-em-disco", r">\s*/dev/(sd|nvme|hd|vd)[a-z]*"),
    ("chmod-777-raiz", r"\bchmod\s+(-R\s+)?777\s+/(\s|$)"),
    ("segredo-em-rede", r"(TOKEN|SECRET|_KEY|PRIVATE_KEY)\b.*\b(curl|wget|nc|socat)\b|\b(curl|wget|nc|socat)\b.*(TOKEN|SECRET|_KEY|PRIVATE_KEY)\b"),
]

_COMPILED = [(name, re.compile(rx, re.IGNORECASE)) for name, rx in _DENY_PATTERNS]


def audit_log(evento: str, registro: Dict[str, Any],
              path: str = "") -> bool:
    """Anexa evento JSONL (best-effort: falha de disco nunca lança)."""
    dest = path or os.environ.get("OPENCODE_HOOKS_AUDIT", _AUDIT_DEFAULT)
    try:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(
                {"ts": datetime.now(timezone.utc).isoformat(),
                 "evento": evento, **registro},
                ensure_ascii=False) + "\n")
        return True
    except OSError:
        return False


def check_bash(command: str) -> Dict[str, Any]:
    """Avalia comando Bash contra a deny-list (puro, sem efeitos)."""
    text = command or ""
    for name, rx in _COMPILED:
        if rx.search(text):
            return {"allow": False, "regra": name,
                    "reason": f"bloqueado pela política ({name})"}
    return {"allow": True, "regra": "", "reason": ""}


def _bash_hook(tool_name: str, args: Dict[str, Any],
               context: Dict[str, Any]) -> Dict[str, Any]:
    """Hook PreToolUse para Bash: nega + audita (auditoria nunca bloqueia)."""
    command = str((args or {}).get("command", ""))
    verdict = check_bash(command)
    audit_log("PreToolUse", {"tool": tool_name, "command": command[:500],
                             "allow": verdict["allow"],
                             "regra": verdict.get("regra", "")})
    if verdict["allow"]:
        return {}
    return {"deny": True, "reason": verdict["reason"]}


def default_matchers() -> List[HookMatcher]:
    """Matchers padrão do Core: guarda Bash + auditoria."""
    return [HookMatcher("Bash", hooks=[_bash_hook])]
