# -*- coding: utf-8 -*-
"""
Engine de hooks do Core (SPEC-935-R653) — roteamento e decisão fail-closed.

Compatível por desenho com a semântica Claude (`PreToolUse`, matchers,
vereditos), sem copiar código: eventos, `HookMatcher` e `run_hooks` são
implementação própria, auditável e sem rede.
"""

from __future__ import annotations

import inspect
import re
from typing import Any, Callable, Dict, List, Optional

EVENTS = ("PreToolUse", "PostToolUse", "SessionStart", "SessionEnd")


class HookMatcher:
    """Casa ferramenta e roteia para hooks: igualdade, prefixo ou `re:…`."""

    def __init__(self, matcher: str, hooks: Optional[List[Callable]] = None):
        self.matcher = matcher
        self.hooks = list(hooks or [])

    def matches(self, tool_name: str) -> bool:
        """True se o matcher casa com a tool (nunca lança)."""
        try:
            if self.matcher.startswith("re:"):
                return re.search(self.matcher[3:], tool_name or "") is not None
            if self.matcher.endswith("*"):
                return (tool_name or "").startswith(self.matcher[:-1])
            return (tool_name or "") == self.matcher
        except re.error:
            return False

    def __repr__(self) -> str:  # pragma: no cover - diagnóstico
        return f"HookMatcher({self.matcher!r}, {len(self.hooks)} hooks)"


def _verdict_of(outcome: Any) -> Optional[str]:
    """Extrai motivo do deny de um retorno de hook; None = allow."""
    if outcome is False:
        return "negado pelo hook"
    if isinstance(outcome, dict):
        if outcome.get("allow") is False:
            return str(outcome.get("reason", "negado pelo hook"))
        specific = outcome.get("hookSpecificOutput")
        if isinstance(specific, dict):
            reason = _verdict_of(specific)
            if reason:
                return reason
        if outcome.get("permissionDecision") == "deny":
            return str(outcome.get("permissionDecisionReason", "negado pelo hook"))
        if outcome.get("deny"):
            return str(outcome.get("reason", "negado pelo hook"))
    return None


def _invoke_hook(fn: Callable, tool_name: str, args: Dict[str, Any],
                 context: Dict[str, Any]) -> Any:
    """Escolhe assinatura antes de chamar; TypeError do corpo não é retry."""
    try:
        signature = inspect.signature(fn)
    except (TypeError, ValueError):
        return fn(tool_name, args, context)
    try:
        signature.bind(tool_name, args, context)
    except TypeError:
        signature.bind(tool_name, args)
        return fn(tool_name, args)
    return fn(tool_name, args, context)


def run_hooks(event: str, tool_name: str = "",
              args: Optional[Dict[str, Any]] = None,
              matchers: Optional[List[HookMatcher]] = None,
              context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Roda hooks do evento; primeiro deny vence (fail-closed, nunca lança)."""
    if event not in EVENTS:
        return {"allow": False, "reason": f"evento de hook desconhecido: {event}"}
    if args is None:
        args = {}
    if not isinstance(args, dict):
        return {"allow": False, "reason": "argumentos de hook devem ser objeto"}
    hook_context = {**(context or {}), "event": event}
    for matcher in matchers or []:
        if not matcher.matches(tool_name):
            continue
        for fn in matcher.hooks:
            try:
                reason = _verdict_of(_invoke_hook(fn, tool_name, args, hook_context))
            except Exception as exc:  # noqa: BLE001 - fail-closed (lição R650)
                return {"allow": False, "reason": f"hook falhou: {exc}"}
            if reason:
                return {"allow": False, "reason": reason}
    return {"allow": True, "reason": ""}
