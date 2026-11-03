# -*- coding: utf-8 -*-
"""Política central de fontes não autorizadas (SPEC-935-R977/R1007).

Fonte única para Python. O plugin TypeScript mantém a mesma lista por não
poder importar Python; os testes cobrem os dois lados.

Uma fonte é bloqueada quando o esquema, o host ou a própria string contêm
marcadores de distribuição não autorizada. A checagem é conservadora: prefere
recusar um falso positivo a permitir uma via irregular.
"""
from __future__ import annotations

from urllib.parse import urlparse

BLOCKED_SUBSTRINGS = ("sci-hub", "scihub")
BLOCKED_SCHEMES = ("scihub-mcp",)


def _norm(value: object) -> str:
    return str(value or "").strip().lower()


def is_blocked_url(value: object) -> bool:
    """True quando a entrada aponta para fonte não autorizada."""
    s = _norm(value)
    if not s:
        return False

    scheme = s.split(":", 1)[0] if ":" in s else ""
    if scheme in BLOCKED_SCHEMES:
        return True

    if any(marker in s for marker in BLOCKED_SUBSTRINGS):
        return True

    try:
        host = (urlparse(s).hostname or "").lower()
    except ValueError:
        host = ""
    return any(marker in host for marker in BLOCKED_SUBSTRINGS)


def assert_allowed_url(value: object) -> str:
    """Devolve a URL original ou levanta PermissionError (fail-closed)."""
    if is_blocked_url(value):
        raise PermissionError(f"blocked: unauthorized_source {value!r}")
    return str(value)


def classify(value: object) -> str:
    """Classificação mínima para relatórios: blocked | allowed."""
    return "blocked" if is_blocked_url(value) else "allowed"
