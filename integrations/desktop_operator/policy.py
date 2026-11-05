"""R1060 — política fechada para o desktop-operator.

O wrapper não aceita argv arbitrário: monta a lista a partir de campos
validados e nega qualquer comando ou flag fora da allowlist. A allowlist de
apps começa vazia; sem ela, snapshot/click/type são negados.
"""

from __future__ import annotations

import json
import os
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

ALLOWED_COMMANDS = frozenset({"status", "list-apps", "snapshot", "click", "type", "wait"})
DENIED_FLAGS = frozenset({
    "--headed", "--force", "--trace", "--trace-file", "--session", "--debug",
    "--cursor-overlay", "--screen", "--screenshot", "--clipboard",
    "--open-system-surface", "--key-down", "--key-up", "--mouse-down",
    "--mouse-up", "--mouse-move", "--mouse-click", "--mouse-wheel",
})
WAIT_PREDICATES = frozenset({"exists", "enabled", "visible", "actionable", "value"})
WAIT_ACTIONS = frozenset({"click", "type", "set-value", "clear"})
APP_RE = re.compile(r"^[A-Za-z0-9._@/-]{1,120}\Z")
REF_RE = re.compile(r"^@[a-z0-9]{6,64}:e[0-9]{1,6}\Z")
DEFAULT_STATE = "~/.local/state/opencode-desktop-operator"
DEFAULT_CACHE_BINARY = "~/.cache/opencode-pilot/desktop-operator/node_modules/.bin/agent-desktop"
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "config/desktop_operator.json"


class PolicyDenied(Exception):
    """Negação determinística com código estável para o chamador."""

    def __init__(self, code: str, reason: str):
        super().__init__(reason)
        self.code = code
        self.reason = reason


@dataclass(frozen=True)
class PolicyConfig:
    binary: str = ""
    allowed_apps: tuple[str, ...] = field(default_factory=tuple)
    state_dir: str = DEFAULT_STATE
    timeout_ms: int = 15000
    max_text_bytes: int = 10000
    max_output_bytes: int = 262144
    approval_ttl_seconds: int = 300

    def __post_init__(self) -> None:
        object.__setattr__(self, "allowed_apps", tuple(str(a) for a in self.allowed_apps))
        for name in ("timeout_ms", "max_text_bytes", "max_output_bytes", "approval_ttl_seconds"):
            value = getattr(self, name)
            if type(value) is not int or value <= 0:
                raise ValueError(f"{name} deve ser inteiro positivo")


def _config_dict(path: Path | None, environ: dict[str, str]) -> dict[str, Any]:
    selected = environ.get("DESKTOP_OPERATOR_CONFIG")
    path = Path(selected).expanduser() if selected else (path or DEFAULT_CONFIG)
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("configuração deve ser objeto JSON")
    allowed = {"binary", "allowed_apps", "state_dir", "timeout_ms", "max_text_bytes",
               "max_output_bytes", "approval_ttl_seconds"}
    unknown = set(data) - allowed
    if unknown:
        raise ValueError(f"chaves desconhecidas na configuração: {sorted(unknown)}")
    return data


def load_config(path: Path | None = None, environ: dict[str, str] | None = None) -> PolicyConfig:
    env = dict(os.environ if environ is None else environ)
    data = _config_dict(path, env)
    apps = data.get("allowed_apps", [])
    if not isinstance(apps, (list, tuple)) or not all(isinstance(a, str) for a in apps):
        raise ValueError("allowed_apps deve ser lista de strings")
    env_apps = env.get("DESKTOP_OPERATOR_ALLOWED_APPS", "").strip()
    if env_apps:
        apps = [item.strip() for item in env_apps.split(",") if item.strip()]
    binary = env.get("DESKTOP_OPERATOR_BIN", "").strip() or str(data.get("binary", "") or "")
    state_dir = env.get("DESKTOP_OPERATOR_STATE_DIR", "").strip() or str(data.get("state_dir", "") or DEFAULT_STATE)
    return PolicyConfig(
        binary=binary,
        allowed_apps=tuple(apps),
        state_dir=state_dir,
        timeout_ms=int(data.get("timeout_ms", 15000)),
        max_text_bytes=int(data.get("max_text_bytes", 10000)),
        max_output_bytes=int(data.get("max_output_bytes", 262144)),
        approval_ttl_seconds=int(data.get("approval_ttl_seconds", 300)),
    )


def resolve_binary(config: PolicyConfig, environ: dict[str, str] | None = None) -> str:
    env = dict(os.environ if environ is None else environ)
    candidate = config.binary.strip() or env.get("DESKTOP_OPERATOR_BIN", "").strip()
    if not candidate:
        cache = Path(DEFAULT_CACHE_BINARY).expanduser()
        candidate = str(cache) if cache.is_file() else (shutil.which("agent-desktop") or "")
    return str(Path(candidate).expanduser()) if candidate else ""


def app_allowed(config: PolicyConfig, app: str) -> bool:
    return app.casefold() in {item.casefold() for item in config.allowed_apps}


def require_app(config: PolicyConfig, app: str | None) -> str:
    if not app:
        raise PolicyDenied("app_required", "app é obrigatório para esta operação")
    if not APP_RE.fullmatch(app):
        raise PolicyDenied("app_invalid", "nome de app inválido")
    if not app_allowed(config, app):
        raise PolicyDenied("app_not_allowed", "app fora da allowlist")
    return app


def require_ref(ref: str | None) -> str:
    if not ref or not REF_RE.fullmatch(ref):
        raise PolicyDenied("ref_invalid", "ref qualificado @<snapshot>:e<N> é obrigatório")
    return ref


def _timeout(value: int | None, config: PolicyConfig, *, minimum: int = 1000, maximum: int = 30000) -> int:
    selected = config.timeout_ms if value is None else value
    if type(selected) is not int or not minimum <= selected <= maximum:
        raise PolicyDenied("timeout_invalid", f"timeout deve estar entre {minimum} e {maximum} ms")
    return selected


def _text(value: str | None, config: PolicyConfig) -> str:
    if not isinstance(value, str) or not value:
        raise PolicyDenied("text_required", "texto é obrigatório")
    raw = value.encode("utf-8")
    if len(raw) > config.max_text_bytes:
        raise PolicyDenied("text_too_large", f"texto excede {config.max_text_bytes} bytes")
    if "\x00" in value:
        raise PolicyDenied("text_invalid", "texto não pode conter NUL")
    if any(ord(ch) < 32 and ch not in "\n\t" for ch in value):
        raise PolicyDenied("text_invalid", "texto contém caractere de controle")
    return value


def build_argv(
    command: str,
    config: PolicyConfig,
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
    wait_mode: str | None = None,
) -> list[str]:
    """Monta argv permitido; qualquer desvio levanta PolicyDenied."""
    if command not in ALLOWED_COMMANDS:
        raise PolicyDenied("command_denied", f"comando fora da allowlist: {command}")
    if wait_mode is not None and wait_mode not in {"ms", "element", "text", "window"}:
        raise PolicyDenied("wait_mode_denied", "modo de espera não exposto")

    if command in {"status", "list-apps"}:
        if any(v is not None for v in (app, ref, text, timeout_ms, max_depth, wait_ms, predicate, value, action, title)):
            raise PolicyDenied("args_denied", f"{command} não aceita argumentos")
        return [command]

    if command == "snapshot":
        target = require_app(config, app)
        depth = 6 if max_depth is None else max_depth
        if type(depth) is not int or not 1 <= depth <= 8:
            raise PolicyDenied("max_depth_invalid", "profundidade deve estar entre 1 e 8")
        return ["snapshot", "--app", target, "-i", "--compact",
                "--max-depth", str(depth), "--timeout-ms", str(_timeout(timeout_ms, config))]

    if command == "click":
        target = require_app(config, app)
        qualified = require_ref(ref)
        return ["click", qualified, "--timeout-ms", str(_timeout(timeout_ms, config))]

    if command == "type":
        target = require_app(config, app)
        qualified = require_ref(ref)
        _text(text, config)
        return ["type", qualified, "--stdin", "--timeout-ms", str(_timeout(timeout_ms, config))]

    if command == "wait":
        modes = [wait_ms is not None, ref is not None, text is not None, title is not None]
        if sum(modes) != 1:
            raise PolicyDenied("wait_mode_invalid", "wait exige exatamente um modo")
        if wait_ms is not None:
            if type(wait_ms) is not int or not 0 <= wait_ms <= 60000:
                raise PolicyDenied("wait_ms_invalid", "espera deve estar entre 0 e 60000 ms")
            return ["wait", str(wait_ms)]
        if ref is not None:
            qualified = require_ref(ref)
            chosen = predicate or "exists"
            if chosen not in WAIT_PREDICATES:
                raise PolicyDenied("predicate_invalid", "predicado não permitido")
            argv = ["wait", "--element", qualified, "--predicate", chosen]
            if chosen == "value":
                if value is None:
                    raise PolicyDenied("value_required", "predicado value exige value")
                argv += ["--value", value]
            elif value is not None:
                raise PolicyDenied("value_denied", "value só é aceito com predicado value")
            if chosen == "actionable":
                argv += ["--action", action or "click"]
                if action is not None and action not in WAIT_ACTIONS:
                    raise PolicyDenied("action_invalid", "ação de espera não permitida")
            elif action is not None:
                raise PolicyDenied("action_denied", "action só é aceita com predicado actionable")
            return argv + ["--timeout", str(_timeout(timeout_ms, config))]
        if text is not None:
            target = require_app(config, app)
            if not text or len(text) > 500:
                raise PolicyDenied("wait_text_invalid", "texto de espera inválido")
            return ["wait", "--text", text, "--app", target, "--timeout", str(_timeout(timeout_ms, config))]
        target = require_app(config, app)
        if not title or len(title) > 200:
            raise PolicyDenied("wait_title_invalid", "título de janela inválido")
        return ["wait", "--window", title, "--app", target, "--timeout", str(_timeout(timeout_ms, config))]

    raise PolicyDenied("command_denied", "comando não implementado")


def guard_argv(argv: Iterable[str], config: PolicyConfig) -> None:
    """Defesa em profundidade para qualquer argv já montado."""
    items = list(argv)
    if not items or items[0] not in ALLOWED_COMMANDS:
        raise PolicyDenied("command_denied", "argv sem comando permitido")
    for item in items:
        if not isinstance(item, str) or "\x00" in item:
            raise PolicyDenied("argv_invalid", "argv contém valor inválido")
        if item in DENIED_FLAGS:
            raise PolicyDenied("flag_denied", f"flag proibida: {item}")
        if item == "--stdin" and items[0] != "type":
            raise PolicyDenied("flag_denied", "--stdin só é permitido em type")
    if items[0] in {"status", "list-apps"} and len(items) != 1:
        raise PolicyDenied("args_denied", f"{items[0]} não aceita argumentos")
