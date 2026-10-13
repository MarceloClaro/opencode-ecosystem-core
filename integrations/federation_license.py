# -*- coding: utf-8 -*-
"""R828 — Triagem de licença fail-closed.

Nunca inventa licença: SPDX ausente permanece degraded.
Operação local, declarativa.
"""

def classify(info):
    """Classifica artefato: ok apenas com SPDX não vazio, senão degraded."""
    if not isinstance(info, dict):
        return "degraded"
    spdx = info.get("spdx")
    if isinstance(spdx, str) and len(spdx.strip()) > 0:
        return "ok"
    return "degraded"
