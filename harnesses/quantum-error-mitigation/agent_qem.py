#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrapper restrito dos agentes de mitigação/correção quântica (R1114).

Permite apenas zne, dd, pec, qec, spam, crosstalk, drift, uncertainty,
lessons e audit. Nenhum comando executa hardware.
"""
from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

from runner import main  # noqa: E402

ALLOWED = {
    "zne", "dd", "dd-pulse", "pec", "qec", "surface",
    "spam", "spam-plan", "spam-separation", "spam-tomography-plan",
    "spam-tomography", "crosstalk",
    "drift", "uncertainty", "preregister", "lessons", "audit",
}
USO = "uso: agent_qem.py <" + "|".join(sorted(ALLOWED)) + "> [args]"


def run(argv: list[str]) -> int:
    if not argv or argv[0] not in ALLOWED:
        print(
            f"blocked: comando {argv[0] if argv else 'ausente'!r} não permitido. {USO}",
            file=sys.stderr,
        )
        return 2
    return main(argv)


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
