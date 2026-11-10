"""Orçamento local por operador para submissões GJQ (R1106).

Não calcula preço em moeda: controla submissões e shots por dia, porque a
plataforma não expõe uma tabela de preço estável no SDK. O ledger é local,
JSONL, com permissão 600, e nunca contém a API key.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_LEDGER = Path.home() / ".gjq_client" / "core_budget_ledger.jsonl"


def _ledger_path(path: str | Path | None = None) -> Path:
    if path is not None:
        return Path(path).expanduser()
    return Path(os.environ.get("GJQ_BUDGET_LEDGER", str(DEFAULT_LEDGER))).expanduser()


def _env_int(name: str, default: int, minimum: int = 0) -> int:
    raw = os.environ.get(name, "")
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return default
    return value if value >= minimum else default


def hardware_enabled() -> bool:
    return os.environ.get("GJQ_HARDWARE_ENABLED", "").strip().lower() in {"1", "true", "yes", "on"}


def budget_limits() -> dict[str, int]:
    return {
        "daily_submissions": _env_int("GJQ_DAILY_SUBMISSIONS", 20, 1),
        "daily_hardware_submissions": _env_int("GJQ_DAILY_HARDWARE_SUBMISSIONS", 1, 0),
        "daily_shots": _env_int("GJQ_DAILY_SHOTS", 100_000, 1),
        "daily_hardware_shots": _env_int("GJQ_DAILY_HARDWARE_SHOTS", 4_096, 0),
    }


def _today_utc() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def read_ledger(path: str | Path | None = None) -> list[dict[str, Any]]:
    ledger = _ledger_path(path)
    if not ledger.is_file():
        return []
    entries: list[dict[str, Any]] = []
    try:
        with ledger.open(encoding="utf-8") as stream:
            for line in stream:
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(item, dict):
                    entries.append(item)
    except OSError:
        return []
    return entries


def usage_today(path: str | Path | None = None, today: str | None = None) -> dict[str, int]:
    dia = today or _today_utc()
    uso = {"submissions": 0, "hardware_submissions": 0, "shots": 0, "hardware_shots": 0}
    for item in read_ledger(path):
        if str(item.get("date", dia)) != dia:
            continue
        try:
            shots = int(item.get("shots", 0))
        except (TypeError, ValueError):
            shots = 0
        if shots < 0:
            shots = 0
        uso["submissions"] += 1
        uso["shots"] += shots
        if item.get("hardware") is True:
            uso["hardware_submissions"] += 1
            uso["hardware_shots"] += shots
    return uso


def _remaining(limits: dict[str, int], usage: dict[str, int]) -> dict[str, int]:
    pares = {
        "daily_submissions": "submissions",
        "daily_hardware_submissions": "hardware_submissions",
        "daily_shots": "shots",
        "daily_hardware_shots": "hardware_shots",
    }
    return {
        limite: max(limits[limite] - usage[uso], 0)
        for limite, uso in pares.items()
    }


def check_budget(backend_name: str, shots: int, hardware: bool,
                 path: str | Path | None = None, today: str | None = None) -> dict[str, Any]:
    if not isinstance(backend_name, str) or not backend_name.strip():
        raise ValueError("backend_name obrigatório")
    if isinstance(shots, bool) or not isinstance(shots, int) or shots < 1:
        raise ValueError("shots deve ser inteiro >= 1")
    limits = budget_limits()
    usage = usage_today(path=path, today=today)
    enabled = hardware_enabled()
    reason = None
    if hardware and not enabled:
        reason = "hardware desabilitado: defina GJQ_HARDWARE_ENABLED=1"
    elif usage["submissions"] >= limits["daily_submissions"]:
        reason = f"limite diário de submissões atingido ({limits['daily_submissions']})"
    elif hardware and usage["hardware_submissions"] >= limits["daily_hardware_submissions"]:
        reason = f"limite diário de submissões de hardware atingido ({limits['daily_hardware_submissions']})"
    elif usage["shots"] + shots > limits["daily_shots"]:
        reason = f"orçamento diário de shots excedido ({usage['shots']} + {shots} > {limits['daily_shots']})"
    elif hardware and usage["hardware_shots"] + shots > limits["daily_hardware_shots"]:
        reason = (
            "orçamento diário de shots de hardware excedido "
            f"({usage['hardware_shots']} + {shots} > {limits['daily_hardware_shots']})"
        )
    return {
        "allowed": reason is None,
        "reason": reason,
        "backend": backend_name,
        "shots": shots,
        "hardware": bool(hardware),
        "hardware_enabled": enabled,
        "usage": usage,
        "limits": limits,
        "remaining": _remaining(limits, usage),
        "executed": False,
    }


def record_submission(backend_name: str, shots: int, task_id: str, hardware: bool,
                      qasm_sha256: str | None = None,
                      path: str | Path | None = None,
                      today: str | None = None) -> dict[str, Any]:
    if not isinstance(backend_name, str) or not backend_name.strip():
        raise ValueError("backend_name obrigatório")
    if isinstance(shots, bool) or not isinstance(shots, int) or shots < 1:
        raise ValueError("shots deve ser inteiro >= 1")
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id obrigatório")
    dia = today or _today_utc()
    ledger = _ledger_path(path)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "date": dia,
        "backend": backend_name,
        "shots": shots,
        "task_id": task_id,
        "hardware": bool(hardware),
        "qasm_sha256": qasm_sha256,
    }
    line = json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n"
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    descriptor = os.open(ledger, flags, 0o600)
    try:
        os.write(descriptor, line.encode("utf-8"))
        try:
            os.fchmod(descriptor, 0o600)
        except (AttributeError, OSError):
            pass
    finally:
        os.close(descriptor)
    return entry


def budget_status(path: str | Path | None = None, today: str | None = None) -> dict[str, Any]:
    limits = budget_limits()
    usage = usage_today(path=path, today=today)
    return {
        "date": today or _today_utc(),
        "hardware_enabled": hardware_enabled(),
        "limits": limits,
        "usage": usage,
        "remaining": _remaining(limits, usage),
        "ledger": str(_ledger_path(path)),
        "note": "Orçamento em submissões/shots; não é preço em moeda.",
        "executed": False,
    }
