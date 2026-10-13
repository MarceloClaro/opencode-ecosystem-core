# -*- coding: utf-8 -*-
"""R832/R836 — consulta somente de leitura ao ledger de ciclos.
Keywords: cycles, cycles.py, cycles.json, evo-, EvolutionCycle. Categoria: cycles_manager."""
from __future__ import annotations
import json
import os
from pathlib import Path
import re


_ROUND_ID = re.compile(r"R([1-9][0-9]*)(?:[a-z]+|-[A-Za-z0-9][A-Za-z0-9._-]*)?")


def next_id(state_path: str | os.PathLike[str] | None = None) -> dict:
    """Consulta max(round numeral)+1, sem reparar nem escrever o histórico.

    Sufixos históricos reservam o numeral. Um ledger ilegível não autoriza
    gerar um identificador. Este cálculo não reserva IDs de specs nem grava
    ciclos; essas operações pertencem a EvolutionRegistry.
    """
    path = Path(state_path) if state_path is not None else Path(
        os.environ.get("EVOLUTION_STATE_PATH", str(Path(__file__).with_name("cycles.json")))
    )
    unavailable = {"next": None, "total": None, "status": "unavailable", "manager": "cycles_manager"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {**unavailable, "error": "ledger_missing"}
    except (OSError, UnicodeError, ValueError):
        return {**unavailable, "error": "ledger_invalid"}
    if not isinstance(data, dict) or not isinstance(data.get("cycles"), list):
        return {**unavailable, "error": "ledger_invalid"}
    cycles = data["cycles"]
    maximum = 0
    for cycle in cycles:
        rid = cycle.get("round_id") if isinstance(cycle, dict) else None
        match = _ROUND_ID.fullmatch(rid) if isinstance(rid, str) else None
        if match is None:
            return {**unavailable, "error": "ledger_invalid"}
        try:
            maximum = max(maximum, int(match.group(1)))
        except ValueError:
            return {**unavailable, "error": "ledger_invalid"}
    return {"next": f"R{maximum + 1}", "total": len(cycles), "status": "ready", "manager": "cycles_manager"}
