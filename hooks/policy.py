# -*- coding: utf-8 -*-
"""
Política padrão de hooks do Core (SPEC-935-R653) — deny-list + auditoria.

Deny-list documentada e testada para Bash destrutivo/exfiltrador. Todo o
resto passa: allowlist total paralisaria o agente; a deny-list é auditável
e evolui por adição (cada item tem teste).
"""

from __future__ import annotations

import hashlib
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


def _audit_safe(value: Any) -> Any:
    """Redige campos sensíveis e substitui comandos por identificação opaca."""
    if isinstance(value, dict):
        safe = {}
        for key, child in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in {"command", "cmd", "script"}:
                command = str(child)
                safe[f"{key}_sha256"] = hashlib.sha256(command.encode()).hexdigest()
                safe[f"{key}_length"] = len(command)
            elif (normalized in {"token", "secret", "password", "passwd", "authorization",
                                 "api_key", "private_key", "credential", "credentials"}
                  or normalized.endswith(("_token", "_secret", "_password", "_api_key", "_private_key"))):
                safe[key] = "[REDACTED]"
            else:
                safe[key] = _audit_safe(child)
        return safe
    if isinstance(value, list):
        return [_audit_safe(child) for child in value]
    return value


def audit_log(evento: str, registro: Dict[str, Any],
              path: str = "") -> bool:
    """Anexa evento JSONL (best-effort: falha de disco nunca lança)."""
    dest = path or os.environ.get("OPENCODE_HOOKS_AUDIT", _AUDIT_DEFAULT)
    try:
        serialized = json.dumps(
            {**_audit_safe(registro), "ts": datetime.now(timezone.utc).isoformat(),
             "evento": evento}, ensure_ascii=False)
        parent = os.path.dirname(dest)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(dest, "a", encoding="utf-8") as fh:
            fh.write(serialized + "\n")
        return True
    except (OSError, TypeError, ValueError, RecursionError):
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
    # Comandos podem conter credenciais ou dados pessoais. Retém somente hash
    # e tamanho para correlação; deny-list é heurística, não sandbox de execução.
    audit_log("PreToolUse", {"tool": tool_name,
                             "command_sha256": hashlib.sha256(command.encode()).hexdigest(),
                             "command_length": len(command),
                             "allow": verdict["allow"],
                             "regra": verdict.get("regra", "")})
    if verdict["allow"]:
        return {}
    return {"deny": True, "reason": verdict["reason"]}


def default_matchers() -> List[HookMatcher]:
    """Matchers padrão do Core: guarda Bash + auditoria."""
    return [HookMatcher("Bash", hooks=[_bash_hook])]
