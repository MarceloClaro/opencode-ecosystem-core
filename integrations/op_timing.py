#!/usr/bin/env python3
"""op_timing — Instrumentação de eficiência por operação (SPEC-975, R582).

Registra duração real de operações do ecossistema (typeof de cada medir:
deploy, smoke, probe, weight, feed, credential, budget, pages_status) em
`.mci_state/op_times.jsonl` (append-only) e gera relatório com mediana/p90.

Uso:
  python3 -m integrations.op_timing record smoke 0.097 ok
  python3 -m integrations.op_timing report [--since ISO]
"""
from __future__ import annotations

import json
import os
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = os.environ.get("MCI_STATE_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".mci_state"))
TIMES_PATH = os.environ.get("OP_TIMES_PATH", os.path.join(STATE_DIR, "op_times.jsonl"))
ROUND_ENV = "OP_ROUND_ID"


def _times_path() -> str:
    """Lê OP_TIMES_PATH em tempo de chamada (testável, respeita overrides)."""
    return os.environ.get("OP_TIMES_PATH", TIMES_PATH)


def record(op: str, seconds: float, ok: bool, round_id: str | None = None) -> None:
    """Append-only: registra uma medição (nunca sobrescreve)."""
    entry = {
        "op": op,
        "seconds": round(float(seconds), 4),
        "ok": bool(ok),
        "round_id": round_id or os.environ.get(ROUND_ENV, "unknown"),
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    path = Path(_times_path())
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def report(since: str | None = None) -> str:
    path = Path(_times_path())
    if not path.is_file():
        return "op_timing: nenhuma medição ainda (arquivo inexistente)"
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if since:
        rows = [r for r in rows if r.get("ts", "") >= since]

    by_op: dict[str, list[float]] = {}
    fails = 0
    for r in rows:
        by_op.setdefault(r.get("op", "?"), []).append(float(r.get("seconds", 0)))
        if not r.get("ok", True):
            fails += 1

    if not by_op:
        return "op_timing: nenhuma medição no período"

    out = [f"op_timing: {len(rows)} medições, {fails} falhas"]
    for op in sorted(by_op):
        vals = sorted(by_op[op])
        med = statistics.median(vals)
        p90 = vals[int(len(vals) * 0.9) - 1] if vals else 0.0
        out.append(
            f"  {op:14s} n={len(vals):3d}  mediana={med*1000:7.1f} ms  p90={p90*1000:7.1f} ms"
        )
    return "\n".join(out)


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "report"
    if cmd == "record":
        if len(argv) < 4:
            print("uso: op_timing record OP SEGUNDOS ok", file=sys.stderr)
            return 2
        record(argv[2], float(argv[3]), argv[4].lower() in {"ok", "1", "true"})
        return 0
    if cmd == "report":
        since = argv[2] if len(argv) > 2 and argv[2].startswith("--since") or (
            len(argv) > 3 and argv[2] == "--since") else None
        if since is None and len(argv) > 2:
            since = argv[2]
        print(report(since))
        return 0
    print(f"comando desconhecido: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))