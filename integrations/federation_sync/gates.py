# -*- coding: utf-8 -*-
"""R1012 — triagem fail-closed de licença, execução e autenticação.

Regra central: ausência de SPDX é ausência de permissão declarada. O item
continua no registro como metadado, mas nunca é materializado nem registrado
como servidor ativo. Nada aqui completa licença por heurística otimista.
"""

from __future__ import annotations

import re
from typing import Iterable, Tuple

# Licenças que o operador pode instalar sem revisão jurídica adicional.
PERMISSIVE = frozenset({
    "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "0BSD",
    "Unlicense", "CC0-1.0", "CC-BY-4.0", "CC-BY-SA-4.0", "MPL-2.0",
})

# Licenças copyleft fortes ou de uso restrito: exigem decisão humana.
REVIEW_REQUIRED = frozenset({
    "GPL-2.0", "GPL-2.0-only", "GPL-2.0-or-later", "GPL-3.0", "GPL-3.0-only",
    "GPL-3.0-or-later", "AGPL-3.0", "AGPL-3.0-only", "AGPL-3.0-or-later",
    "LGPL-2.1", "LGPL-3.0", "BUSL-1.1", "SSPL-1.0", "Elastic-2.0",
    "Commons-Clause", "Proprietary",
})

_TEXT_RULES = (
    (re.compile(r"apache license", re.I), "Apache-2.0"),
    (re.compile(r"\bmit license\b|\bpermission is hereby granted, free of charge\b", re.I), "MIT"),
    (re.compile(r"bsd 3-clause|redistribution and use in source and binary forms.*neither the name", re.I | re.S), "BSD-3-Clause"),
    (re.compile(r"bsd 2-clause|redistribution and use in source and binary forms", re.I | re.S), "BSD-2-Clause"),
    (re.compile(r"gnu affero general public license.*version 3", re.I | re.S), "AGPL-3.0"),
    (re.compile(r"gnu general public license.*version 3", re.I | re.S), "GPL-3.0"),
    (re.compile(r"gnu general public license.*version 2", re.I | re.S), "GPL-2.0"),
    (re.compile(r"mozilla public license.*2\.0", re.I | re.S), "MPL-2.0"),
    (re.compile(r"business source license", re.I), "BUSL-1.1"),
)


def normalize_license(raw: str) -> str:
    """Normaliza um SPDX declarado; devolve ``''`` quando não há declaração."""

    text = (raw or "").strip()
    if not text:
        return ""
    lowered = text.lower()
    if lowered in {"unknown", "none", "n/a", "na", "see license", "proprietary"}:
        return "" if lowered != "proprietary" else "Proprietary"
    for canonical in sorted(PERMISSIVE | REVIEW_REQUIRED, key=len, reverse=True):
        if lowered == canonical.lower():
            return canonical
    if "apache" in lowered:
        return "Apache-2.0"
    if re.search(r"\bmit\b", lowered):
        return "MIT"
    if "bsd" in lowered and "3" in lowered:
        return "BSD-3-Clause"
    if "bsd" in lowered:
        return "BSD-2-Clause"
    if "agpl" in lowered:
        return "AGPL-3.0"
    if "lgpl" in lowered:
        return "LGPL-3.0"
    if "gpl" in lowered:
        return "GPL-3.0"
    return text[:80]


def license_from_text(text: str) -> str:
    """Reconhece SPDX a partir do texto de um arquivo LICENSE."""

    head = (text or "")[:6000]
    for pattern, canonical in _TEXT_RULES:
        if pattern.search(head):
            return canonical
    return ""


def classify(
    *,
    kind: str,
    license: str,
    install_mode: str,
    auth_required: bool = False,
    hosted_connector: bool = False,
    has_scripts: bool = False,
) -> Tuple[str, Tuple[str, ...], str]:
    """
    Devolve ``(status, motivos, risco_de_runtime)``.

    A ordem importa: bloqueio de execução vence tudo; licença ausente vence
    autenticação; por último, o item que exige decisão humana fica em quarentena.
    """

    reasons = []

    if kind == "hook" or has_scripts:
        reasons.append("third_party_execution")
    if not license:
        reasons.append("license_undeclared")
    elif license in REVIEW_REQUIRED:
        reasons.append("license_review_required")
    if hosted_connector or install_mode == "external":
        reasons.append("not_locally_installable")
    if auth_required:
        reasons.append("auth_required")

    if "third_party_execution" in reasons:
        status = "blocked"
    elif "license_undeclared" in reasons:
        status = "degraded"
    elif reasons:
        status = "quarantined"
    else:
        status = "admitted"

    if kind == "mcp":
        risk = "process"
    elif kind in {"hook", "plugin"} and has_scripts:
        risk = "exec"
    elif hosted_connector:
        risk = "network"
    else:
        risk = "none"
    return status, tuple(reasons), risk


def summarize(items: Iterable) -> dict:
    """Contagem por estado/motivo, usada no relatório e nos testes."""

    by_status = {}
    by_reason = {}
    for item in items:
        by_status[item.status] = by_status.get(item.status, 0) + 1
        for reason in item.reasons:
            by_reason[reason] = by_reason.get(reason, 0) + 1
    return {
        "by_status": dict(sorted(by_status.items())),
        "by_reason": dict(sorted(by_reason.items())),
    }
