"""R1060 — execução confinada do agent-desktop e redação de resultados."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any

from . import approvals, policy

SENSITIVE_KEYS = frozenset({
    "password", "passwd", "secret", "token", "authorization", "cookie",
    "api_key", "apikey", "access_token", "refresh_token", "private_key",
})
REDACTIONS = (
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "[REDACTED_EMAIL]"),
    (re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"), "[REDACTED_CPF]"),
    (re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b"), "[REDACTED_CNPJ]"),
    (re.compile(r"\b(?:\d[ -]?){13,19}\b"), "[REDACTED_CARD]"),
    (re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/-]+=*"), "[REDACTED_BEARER]"),
    (re.compile(r"\b[a-fA-F0-9]{32,}\b"), "[REDACTED_HEX]"),
    (re.compile(r"\b[A-Za-z0-9+/_-]{40,}={0,2}\b"), "[REDACTED_BLOB]"),
)
ENV_ALLOWLIST = ("PATH", "HOME", "DISPLAY", "WAYLAND_DISPLAY", "XDG_RUNTIME_DIR",
                 "DBUS_SESSION_BUS_ADDRESS", "LANG", "LC_ALL", "TMPDIR")


def minimal_env(environ: dict[str, str] | None = None) -> dict[str, str]:
    source = os.environ if environ is None else environ
    env = {key: source[key] for key in ENV_ALLOWLIST if key in source}
    env["NO_COLOR"] = "1"
    return env


def _redact_string(value: str) -> str:
    result = value
    for pattern, replacement in REDACTIONS:
        result = pattern.sub(replacement, result)
    return result


def redact_payload(value: Any, key: str | None = None) -> Any:
    if isinstance(value, dict):
        return {
            k: "[REDACTED]" if str(k).casefold() in SENSITIVE_KEYS else redact_payload(v, str(k))
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [redact_payload(item) for item in value]
    if isinstance(value, tuple):
        return [redact_payload(item) for item in value]
    if isinstance(value, str):
        if key and key.casefold() in SENSITIVE_KEYS:
            return "[REDACTED]"
        return _redact_string(value)
    return value


def _shrink(value: Any, string_limit: int, list_limit: int, depth: int = 0) -> Any:
    if depth > 40:
        return "[DEPTH_LIMIT]"
    if isinstance(value, dict):
        items = list(value.items())[:list_limit]
        result = {k: _shrink(v, string_limit, list_limit, depth + 1) for k, v in items}
        if len(value) > len(items):
            result["_truncated_keys"] = len(value) - len(items)
        return result
    if isinstance(value, list):
        items = value[:list_limit]
        result = [_shrink(item, string_limit, list_limit, depth + 1) for item in items]
        if len(value) > len(items):
            result.append({"_truncated_items": len(value) - len(items)})
        return result
    if isinstance(value, str) and len(value) > string_limit:
        return value[:string_limit] + "…[TRUNCATED]"
    return value


def limit_payload(value: Any, max_bytes: int) -> tuple[Any, bool]:
    if max_bytes < 256:
        max_bytes = 256
    encoded = json.dumps(value, ensure_ascii=False).encode("utf-8")
    if len(encoded) <= max_bytes:
        return value, False
    for string_limit, list_limit in ((2000, 200), (800, 80), (300, 30), (120, 12), (40, 5)):
        candidate = _shrink(value, string_limit, list_limit)
        if len(json.dumps(candidate, ensure_ascii=False).encode("utf-8")) <= max_bytes:
            return candidate, True
    fallback = {"truncated": True, "message": "resposta excede o limite local", "sha256": hashlib.sha256(encoded).hexdigest()}
    return fallback, True


def _parse_envelope(stdout: str) -> dict:
    text = stdout.strip()
    if not text:
        raise ValueError("stdout vazio")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = json.loads(text.splitlines()[-1])
    if not isinstance(parsed, dict):
        raise ValueError("envelope não é objeto")
    return parsed


def _denied(code: str, reason: str, command: str, *, app: str | None = None) -> dict:
    return {
        "ok": False,
        "command": command,
        "error": {"code": code, "message": reason},
        "policy": {
            "allowed": False,
            "command": command,
            "app": app,
            "code": code,
            "reason": reason,
            "external_validation": False,
        },
    }


def run(
    command: str,
    config: policy.PolicyConfig | None = None,
    *,
    app: str | None = None,
    ref: str | None = None,
    text: str | None = None,
    timeout_ms: int | None = None,
    max_depth: int | None = None,
    wait_ms: int | None = None,
    predicate: str | None = None,
    value: str | None = None,
    action: str | None = None,
    title: str | None = None,
    approval_token: str | None = None,
) -> dict:
    selected = config or policy.load_config()
    try:
        argv = policy.build_argv(
            command, selected, app=app, ref=ref, text=text, timeout_ms=timeout_ms,
            max_depth=max_depth, wait_ms=wait_ms, predicate=predicate, value=value,
            action=action, title=title,
        )
        policy.guard_argv(argv, selected)
    except policy.PolicyDenied as exc:
        return _denied(exc.code, exc.reason, command, app=app)

    binary = policy.resolve_binary(selected)
    if not binary or not Path(binary).is_file() or not os.access(binary, os.X_OK):
        return _denied("binary_not_found", "agent-desktop não instalado no caminho configurado", command, app=app)

    approval_used = False
    if command in {"click", "type"}:
        if not approval_token:
            return _denied("approval_required", "aprovação humana obrigatória", command, app=app)
        try:
            approvals.verify_approval(
                selected, approval_token, command, app or "", ref or "", text=text
            )
            approval_used = True
        except approvals.ApprovalError as exc:
            return _denied(exc.code, exc.reason, command, app=app)

    state_dir = Path(selected.state_dir).expanduser()
    try:
        state_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        return _denied("state_dir_error", "diretório de estado indisponível", command, app=app)
    started = time.monotonic()
    try:
        completed = subprocess.run(
            [binary, *argv],
            input=text if command == "type" else None,
            text=True,
            capture_output=True,
            timeout=min(120.0, selected.timeout_ms / 1000 + 10.0),
            env=minimal_env(),
            cwd=state_dir,
            shell=False,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return _denied("timeout", "agent-desktop excedeu o tempo local", command, app=app)
    except OSError as exc:
        return _denied("exec_failed", f"falha ao executar: {exc.__class__.__name__}", command, app=app)
    duration_ms = round((time.monotonic() - started) * 1000)

    try:
        envelope = _parse_envelope(completed.stdout)
    except (ValueError, json.JSONDecodeError):
        stderr = _redact_string(completed.stderr[-2000:])
        return {
            "ok": False,
            "command": command,
            "error": {"code": "invalid_json", "message": "saída do agent-desktop não é JSON", "stderr": stderr},
            "policy": {
                "allowed": True, "command": command, "app": app,
                "approval_used": approval_used, "duration_ms": duration_ms,
                "external_validation": False,
            },
        }

    redacted = redact_payload(envelope)
    limited, truncated = limit_payload(redacted, selected.max_output_bytes)
    if isinstance(limited, dict):
        limited["policy"] = {
            "allowed": True,
            "command": command,
            "app": app,
            "approval_used": approval_used,
            "duration_ms": duration_ms,
            "truncated": truncated,
            "external_validation": False,
        }
        limited.setdefault("ok", bool(envelope.get("ok")))
    return limited
