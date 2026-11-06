"""R1063 — ponte Python para UI Automation do Windows.

Ações são permitidas apenas em janelas allowlisted e exigem `confirmed=True`.
Texto e árvore passam por redação; nada de shell ou scripts arbitrários.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from integrations.desktop_operator import runtime as redaction

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "config/accessible_assistant.json"


class UIAError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def load_config(path: Path | None = None) -> dict:
    target = Path(path).expanduser() if path else DEFAULT_CONFIG
    data = json.loads(target.read_text(encoding="utf-8")) if target.is_file() else {}
    data.setdefault("bridge_path", r"C:\Users\marce\AppData\Local\Temp\opencode-uia.ps1")
    data.setdefault("allowed_windows", [])
    data.setdefault("denied_windows", [])
    data.setdefault("max_depth", 6)
    data.setdefault("timeout_seconds", 30)
    return data


def window_allowed(config: dict, window: str) -> bool:
    name = (window or "").casefold()
    if not name:
        return False
    if any(pattern.casefold() in name for pattern in config.get("denied_windows", [])):
        return False
    return any(pattern.casefold() in name for pattern in config.get("allowed_windows", []))


def window_readable(config: dict, window: str) -> bool:
    name = (window or "").casefold()
    if not name:
        return False
    if any(pattern.casefold() in name for pattern in config.get("denied_windows", [])):
        return False
    if window_allowed(config, window):
        return True
    return any(pattern.casefold() in name for pattern in config.get("read_only_windows", []))


def _powershell(command: str, config: dict, *, window: str = "", name: str = "",
                value: str = "", max_depth: int | None = None) -> dict:
    argv = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", config["bridge_path"], "-Command", command]
    if window:
        argv += ["-Window", window]
    if name:
        argv += ["-Name", name]
    if value:
        argv += ["-Value", value]
    if max_depth is not None:
        argv += ["-MaxDepth", str(max_depth)]
    try:
        result = subprocess.run(argv, capture_output=True, text=True,
                                timeout=config.get("timeout_seconds", 30),
                                shell=False, check=False)
    except subprocess.TimeoutExpired as exc:
        raise UIAError("TIMEOUT", "UI Automation excedeu o tempo") from exc
    except OSError as exc:
        raise UIAError("POWERSHELL_NOT_FOUND", "powershell.exe indisponível") from exc
    text = (result.stdout or "").strip()
    if not text:
        raise UIAError("EMPTY_OUTPUT", (result.stderr or "sem saída")[-500:])
    try:
        envelope = json.loads(text)
    except json.JSONDecodeError as exc:
        raise UIAError("INVALID_JSON", text[-500:]) from exc
    sanitized, warnings = redaction.sanitize_payload(envelope)
    redacted = redaction.redact_payload(sanitized)
    limited, truncated = redaction.limit_payload(redacted, 262144)
    if isinstance(limited, dict):
        limited["untrusted_warnings"] = warnings[:10]
        limited["truncated"] = truncated
    return limited


def list_windows(config: dict | None = None) -> dict:
    config = config or load_config()
    result = _powershell("list-windows", config)
    if result.get("ok") and isinstance(result.get("data"), list):
        for item in result["data"]:
            item["allowed"] = window_allowed(config, item.get("name", ""))
            item["read_only"] = window_readable(config, item.get("name", "")) and not item["allowed"]
    return result


def _resolve_window(config: dict, window: str, *, write: bool = True) -> str:
    result = _powershell("list-windows", config)
    names = [item.get("name", "") for item in result.get("data", []) if item.get("name")]
    matches = [name for name in names if window.casefold() in name.casefold()]
    if not matches:
        raise UIAError("WINDOW_NOT_FOUND", "janela não encontrada")
    if len(matches) > 1:
        raise UIAError("AMBIGUOUS_WINDOW", "mais de uma janela corresponde")
    full = matches[0]
    allowed = window_allowed(config, full) if write else window_readable(config, full)
    if not allowed:
        raise UIAError("WINDOW_NOT_ALLOWED", "janela fora da allowlist")
    return full


def snapshot(window: str, config: dict | None = None) -> dict:
    config = config or load_config()
    window = _resolve_window(config, window, write=False)
    return _powershell("snapshot", config, window=window,
                       max_depth=min(int(config.get("max_depth", 6)), 6))


def read(window: str, config: dict | None = None) -> dict:
    config = config or load_config()
    window = _resolve_window(config, window, write=False)
    return _powershell("read", config, window=window)


def read_text(window: str, config: dict | None = None) -> dict:
    config = config or load_config()
    window = _resolve_window(config, window, write=False)
    return _powershell("read-text", config, window=window)


def read_text_focused(config: dict | None = None) -> dict:
    config = config or load_config()
    result = _powershell("focused", config)
    window = (result.get("data") or {}).get("window", "")
    if not window_readable(config, window):
        raise UIAError("WINDOW_NOT_ALLOWED", "janela em foco fora da leitura permitida")
    return read_text(window, config)


def focus(window: str, config: dict | None = None) -> dict:
    config = config or load_config()
    window = _resolve_window(config, window)
    return _powershell("focus", config, window=window)


def invoke(window: str, name: str, *, confirmed: bool = False,
           config: dict | None = None) -> dict:
    config = config or load_config()
    window = _resolve_window(config, window)
    if not confirmed:
        raise UIAError("CONFIRMATION_REQUIRED", "confirmação explícita obrigatória")
    return _powershell("invoke", config, window=window, name=name)


def set_value(window: str, name: str, value: str, *, confirmed: bool = False,
              config: dict | None = None) -> dict:
    config = config or load_config()
    window = _resolve_window(config, window)
    if not confirmed:
        raise UIAError("CONFIRMATION_REQUIRED", "confirmação explícita obrigatória")
    if not isinstance(value, str) or len(value) > 2000 or "\x00" in value:
        raise UIAError("VALUE_INVALID", "texto inválido ou acima de 2000 caracteres")
    return _powershell("set-value", config, window=window, name=name, value=value)


def focused(config: dict | None = None) -> dict:
    config = config or load_config()
    result = _powershell("focused", config)
    window = (result.get("data") or {}).get("window", "")
    if result.get("ok") and not window_allowed(config, window):
        raise UIAError("WINDOW_NOT_ALLOWED", "janela em foco fora da allowlist")
    return result


def set_focused(value: str, *, confirmed: bool = False,
                config: dict | None = None) -> dict:
    config = config or load_config()
    if not confirmed:
        raise UIAError("CONFIRMATION_REQUIRED", "confirmação explícita obrigatória")
    if not isinstance(value, str) or len(value) > 2000 or "\x00" in value:
        raise UIAError("VALUE_INVALID", "texto inválido ou acima de 2000 caracteres")
    result = _powershell("focused", config)
    window = (result.get("data") or {}).get("window", "")
    if not window_allowed(config, window):
        raise UIAError("WINDOW_NOT_ALLOWED", "janela em foco fora da allowlist")
    return _powershell("set-focused", config, value=value)


def invoke_focused(*, confirmed: bool = False, config: dict | None = None) -> dict:
    config = config or load_config()
    if not confirmed:
        raise UIAError("CONFIRMATION_REQUIRED", "confirmação explícita obrigatória")
    result = _powershell("focused", config)
    window = (result.get("data") or {}).get("window", "")
    if not window_allowed(config, window):
        raise UIAError("WINDOW_NOT_ALLOWED", "janela em foco fora da allowlist")
    return _powershell("invoke-focused", config)
