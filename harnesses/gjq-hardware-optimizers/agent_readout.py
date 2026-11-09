#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrapper restrito do agente gjq-readout-mitigation (R1111).

Permite apenas:

    agent_readout.py compare-plan ...   -> runner.py compare --plan ...
    agent_readout.py mitigate ...       -> runner.py mitigate ...

Rejeita ``run``, ``compare`` direto e qualquer outro comando. A submissão de
hardware permanece no primário, com ``--confirm`` e ``--allow-hardware``.
"""
from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

from runner import main  # noqa: E402

USO = (
    "uso: agent_readout.py compare-plan [args de compare] | "
    "agent_readout.py mitigate [args de mitigate]"
)


def run(argv: list[str]) -> int:
    if not argv:
        print(USO, file=sys.stderr)
        return 2
    command = argv[0]
    if command == "compare-plan":
        return main(["compare", "--plan", *argv[1:]])
    if command == "mitigate":
        return main(["mitigate", *argv[1:]])
    print(
        f"blocked: comando {command!r} não permitido; este agente só planeja "
        "comparação e mitiga leitura offline. Hardware exige o primário.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
