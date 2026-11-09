#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrapper restrito do agente gjq-readout-mitigation (R1111).

Permite apenas:

    compare-plan  -> runner.py compare --plan
    mitigate      -> runner.py mitigate
    loop-plan     -> loop_runner.py plan
    loop-simulate -> loop_runner.py simulate
    loop-execute  -> loop_runner.py execute
    loop-score    -> loop_runner.py score
    loop-run      -> loop_runner.py run
    loop-status   -> loop_runner.py status
    loop-report   -> loop_runner.py report

Rejeita ``run``, ``compare`` direto e qualquer outro comando. O hardware do
loop exige gates SDD/TDD/simulação e ``--confirm --allow-hardware``.
"""
from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

from loop_runner import main as loop_main  # noqa: E402
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
    loop_map = {
        "loop-plan": ["plan"],
        "loop-simulate": ["simulate"],
        "loop-execute": ["execute"],
        "loop-score": ["score"],
        "loop-run": ["run"],
        "loop-status": ["status"],
        "loop-report": ["report"],
    }
    if command in loop_map:
        return loop_main([*loop_map[command], *argv[1:]])
    print(
        f"blocked: comando {command!r} não permitido; este agente só planeja "
        "comparação e mitiga leitura offline. Hardware exige o primário.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
