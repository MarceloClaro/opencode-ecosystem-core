"""R1060 — backend AT-SPI local para Linux.

Fallback quando o binário upstream falha com `native_window_unproven`. Lê a
árvore de acessibilidade e executa ações semânticas via AT-SPI, mantendo o
mesmo contrato de refs do wrapper. Não usa clipboard, screenshot ou mouse.
"""

from __future__ import annotations

import json
import os
import secrets
import time
from pathlib import Path
from typing import Any

VERSION = "r1060-atspi/1"
MAX_NODES = 2000
MAX_NAME = 500
MAX_VALUE = 2000


class AtspiError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def _atspi():
    try:
        import gi
        gi.require_version("Atspi", "2.0")
        from gi.repository import Atspi
        return Atspi
    except Exception as exc:  # pragma: no cover - depende do host
        raise AtspiError("ATSPI_UNAVAILABLE", f"AT-SPI indisponível: {exc}") from exc


def available() -> bool:
    try:
        _atspi()
        return True
    except AtspiError:
        return False


def _apps(Atspi) -> list[Any]:
    desktop = Atspi.get_desktop(0)
    return [desktop.get_child_at_index(i) for i in range(desktop.get_child_count())]


def _find_app(Atspi, name: str, pid: int | None = None):
    matches = []
    for app in _apps(Atspi):
        try:
            if str(app.get_name()).casefold() != name.casefold():
                continue
            if pid is not None and _pid(app) != pid:
                continue
            matches.append(app)
        except Exception:
            continue
    if not matches:
        raise AtspiError("APP_NOT_FOUND", f"app não encontrado: {name}")
    if len(matches) > 1:
        raise AtspiError("AMBIGUOUS_TARGET", f"mais de um app com o nome {name}")
    return matches[0]


def _pid(node) -> int | None:
    try:
        value = node.get_process_id()
        return int(value) if value is not None else None
    except Exception:
        return None


def _role(node) -> str:
    try:
        return str(node.get_role_name() or "")
    except Exception:
        return ""


def _name(node) -> str:
    try:
        text = str(node.get_name() or "")
    except Exception:
        text = ""
    return text[:MAX_NAME]


def _text_value(node) -> str | None:
    try:
        Atspi = _atspi()
        if node.is_text():
            text = Atspi.Text.get_text(node, 0, -1)
            if text:
                return str(text)[:MAX_VALUE]
    except Exception:
        pass
    try:
        if node.is_value():
            value = node.get_value()
            if value is not None:
                return str(value)[:MAX_VALUE]
    except Exception:
        pass
    return None


def _state_set(node):
    try:
        return node.get_state_set()
    except Exception:
        return None


def _has_state(Atspi, node, name: str) -> bool:
    states = _state_set(node)
    if states is None:
        return False
    try:
        kind = getattr(Atspi.StateType, name)
        return bool(states.contains(kind))
    except Exception:
        return False


def _actionable(node) -> bool:
    try:
        iface = node.get_action_iface()
        return bool(iface is not None and iface.get_n_actions() > 0)
    except Exception:
        return False


def _editable(node) -> bool:
    try:
        return bool(node.is_editable_text() and node.get_editable_text_iface() is not None)
    except Exception:
        return False


def _children(node) -> list[Any]:
    try:
        return [node.get_child_at_index(i) for i in range(node.get_child_count())]
    except Exception:
        return []


def _store_dir(config) -> Path:
    path = Path(config.state_dir).expanduser() / "atspi-refs"
    path.mkdir(parents=True, exist_ok=True)
    try:
        path.chmod(0o700)
    except OSError:
        pass
    return path


def _store_path(config, snapshot_id: str) -> Path:
    if not snapshot_id or not snapshot_id.isalnum():
        raise AtspiError("SNAPSHOT_NOT_FOUND", "snapshot inválido")
    return _store_dir(config) / f"{snapshot_id}.json"


def owns_ref(config, ref: str) -> bool:
    try:
        snapshot_id = ref.split(":", 1)[0].lstrip("@")
        return _store_path(config, snapshot_id).is_file()
    except Exception:
        return False


def _serialize(Atspi, node, path: list[int], snapshot_id: str, refs: dict,
               depth: int, max_depth: int, budget: dict) -> dict | None:
    if budget["nodes"] <= 0:
        budget["truncated"] = True
        return None
    budget["nodes"] -= 1
    item: dict[str, Any] = {"role": _role(node), "name": _name(node)}
    value = _text_value(node)
    if value:
        item["value"] = value
    action = _actionable(node)
    editable = _editable(node)
    if action or editable:
        ref = f"@{snapshot_id}:e{len(refs) + 1}"
        refs[ref] = {"path": path, "role": item["role"], "name": item["name"],
                     "actionable": action, "editable": editable}
        item["ref_id"] = ref
    states = []
    for state in ("ENABLED", "VISIBLE", "FOCUSED"):
        if _has_state(Atspi, node, state):
            states.append(state.casefold())
    if states:
        item["states"] = states
    if depth < max_depth:
        children = []
        for index, child in enumerate(_children(node)):
            serialized = _serialize(Atspi, child, path + [index], snapshot_id,
                                    refs, depth + 1, max_depth, budget)
            if serialized is not None:
                children.append(serialized)
        if children:
            item["children"] = children
    elif _children(node):
        budget["truncated"] = True
    return item


def _walk(node):
    yield node
    for child in _children(node):
        yield from _walk(child)


def _contains_text(node, needle: str) -> bool:
    target = needle.casefold()
    for item in _walk(node):
        if target in _name(item).casefold():
            return True
        value = _text_value(item)
        if value and target in value.casefold():
            return True
    return False


def status(config) -> dict:
    try:
        Atspi = _atspi()
        apps = _apps(Atspi)
        return {"version": VERSION, "ok": True, "command": "status",
                "data": {"platform": "linux", "backend": "atspi",
                         "accessibility": {"state": "granted"},
                         "scope": {"linux_apps": True, "windows_apps": False,
                                   "note": "WSL enxerga apps Linux do WSLg; apps Windows exigem binário no host."},
                         "apps": len(apps), "ref_count": None},
                "policy": {"backend": "atspi", "external_validation": False}}
    except AtspiError as exc:
        return {"version": VERSION, "ok": False, "command": "status",
                "error": {"code": exc.code, "message": exc.message},
                "policy": {"backend": "atspi", "external_validation": False}}


def list_apps(config) -> dict:
    try:
        Atspi = _atspi()
        apps = [{"name": _name(app), "pid": _pid(app), "role": _role(app),
                 "children": len(_children(app))} for app in _apps(Atspi)]
        return {"version": VERSION, "ok": True, "command": "list-apps",
                "data": {"apps": apps},
                "policy": {"backend": "atspi", "external_validation": False}}
    except AtspiError as exc:
        return {"version": VERSION, "ok": False, "command": "list-apps",
                "error": {"code": exc.code, "message": exc.message},
                "policy": {"backend": "atspi", "external_validation": False}}


def snapshot(config, app: str, max_depth: int = 6) -> dict:
    try:
        Atspi = _atspi()
        application = _find_app(Atspi, app)
        snapshot_id = secrets.token_hex(4)
        refs: dict[str, dict] = {}
        budget = {"nodes": MAX_NODES, "truncated": False}
        tree = _serialize(Atspi, application, [], snapshot_id, refs, 0,
                          max(1, min(int(max_depth), 8)), budget)
        payload = {"app": _name(application), "pid": _pid(application),
                   "snapshot_id": snapshot_id, "refs": refs}
        target = _store_path(config, snapshot_id)
        descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False)
        return {"version": VERSION, "ok": True, "command": "snapshot",
                "data": {"app": payload["app"], "snapshot_id": snapshot_id,
                         "ref_count": len(refs), "complete": not budget["truncated"],
                         "truncated": budget["truncated"], "backend": "atspi",
                         "tree": tree},
                "policy": {"backend": "atspi", "external_validation": False}}
    except AtspiError as exc:
        return {"version": VERSION, "ok": False, "command": "snapshot",
                "error": {"code": exc.code, "message": exc.message},
                "policy": {"backend": "atspi", "external_validation": False}}


def _resolve(config, app: str, ref: str):
    snapshot_id = ref.split(":", 1)[0].lstrip("@")
    target = _store_path(config, snapshot_id)
    if not target.is_file():
        raise AtspiError("SNAPSHOT_NOT_FOUND", "snapshot não encontrado")
    payload = json.loads(target.read_text(encoding="utf-8"))
    if str(payload.get("app", "")).casefold() != app.casefold():
        raise AtspiError("APP_MISMATCH", "ref pertence a outro app")
    entry = (payload.get("refs") or {}).get(ref)
    if not entry:
        raise AtspiError("STALE_REF", "ref não existe no snapshot")
    Atspi = _atspi()
    node = _find_app(Atspi, app, payload.get("pid"))
    for index in entry["path"]:
        node = node.get_child_at_index(index)
        if node is None:
            raise AtspiError("STALE_REF", "caminho do ref não resolve")
    return node, entry


def click(config, app: str, ref: str) -> dict:
    try:
        node, _ = _resolve(config, app, ref)
        iface = node.get_action_iface()
        if iface is None or iface.get_n_actions() < 1:
            raise AtspiError("ACTION_NOT_SUPPORTED", "elemento sem ação")
        delivered = bool(iface.do_action(0))
        return {"version": VERSION, "ok": delivered, "command": "click",
                "data": {"action": "click", "backend": "atspi", "ref": ref,
                         "disposition": {"delivery": "delivered_unverified" if delivered else "not_delivered",
                                         "retry": "unsafe" if delivered else "safe"}},
                "policy": {"backend": "atspi", "external_validation": False}}
    except AtspiError as exc:
        return {"version": VERSION, "ok": False, "command": "click",
                "error": {"code": exc.code, "message": exc.message},
                "policy": {"backend": "atspi", "external_validation": False}}


def type_text(config, app: str, ref: str, text: str) -> dict:
    try:
        node, _ = _resolve(config, app, ref)
        iface = node.get_editable_text_iface()
        if iface is None:
            raise AtspiError("ACTION_NOT_SUPPORTED", "elemento não editável")
        iface.set_text_contents(text)
        observed = _text_value(node)
        verified = observed == text
        return {"version": VERSION, "ok": True, "command": "type",
                "data": {"action": "type", "backend": "atspi", "ref": ref,
                         "post_state": {"value": observed} if observed is not None else {},
                         "disposition": {"delivery": "delivered_verified" if verified else "delivered_unverified",
                                         "retry": "unsafe"}},
                "policy": {"backend": "atspi", "external_validation": False}}
    except AtspiError as exc:
        return {"version": VERSION, "ok": False, "command": "type",
                "error": {"code": exc.code, "message": exc.message},
                "policy": {"backend": "atspi", "external_validation": False}}


def _predicate(node, predicate: str, value: str | None) -> bool:
    if predicate == "exists":
        return True
    if predicate == "visible":
        return _has_state(_atspi(), node, "VISIBLE")
    if predicate == "enabled":
        return _has_state(_atspi(), node, "ENABLED")
    if predicate == "actionable":
        return _actionable(node) or _editable(node)
    if predicate == "value":
        return _text_value(node) == value
    return False


def wait(config, *, app: str | None = None, ref: str | None = None,
         text: str | None = None, wait_ms: int | None = None,
         predicate: str | None = None, value: str | None = None,
         timeout_ms: int = 5000) -> dict:
    started = time.monotonic()
    try:
        if wait_ms is not None:
            time.sleep(max(0, min(int(wait_ms), 60000)) / 1000)
            return {"version": VERSION, "ok": True, "command": "wait",
                    "data": {"waited_ms": wait_ms},
                    "policy": {"backend": "atspi", "external_validation": False}}
        if not app:
            raise AtspiError("APP_REQUIRED", "app é obrigatório")
        deadline = started + max(1, min(int(timeout_ms), 30000)) / 1000
        while time.monotonic() <= deadline:
            try:
                if ref:
                    node, _ = _resolve(config, app, ref)
                    if _predicate(node, predicate or "exists", value):
                        return {"version": VERSION, "ok": True, "command": "wait",
                                "data": {"found": True, "elapsed_ms": round((time.monotonic() - started) * 1000)},
                                "policy": {"backend": "atspi", "external_validation": False}}
                elif text:
                    Atspi = _atspi()
                    if _contains_text(_find_app(Atspi, app), text):
                        return {"version": VERSION, "ok": True, "command": "wait",
                                "data": {"found": True, "elapsed_ms": round((time.monotonic() - started) * 1000)},
                                "policy": {"backend": "atspi", "external_validation": False}}
            except AtspiError:
                pass
            time.sleep(0.1)
        raise AtspiError("TIMEOUT", "condição de espera não satisfeita")
    except AtspiError as exc:
        return {"version": VERSION, "ok": False, "command": "wait",
                "error": {"code": exc.code, "message": exc.message},
                "policy": {"backend": "atspi", "external_validation": False}}


def run(command: str, config, **kwargs) -> dict:
    if command == "status":
        return status(config)
    if command == "list-apps":
        return list_apps(config)
    if command == "snapshot":
        return snapshot(config, kwargs.get("app") or "", kwargs.get("max_depth", 6))
    if command == "click":
        return click(config, kwargs.get("app") or "", kwargs.get("ref") or "")
    if command == "type":
        return type_text(config, kwargs.get("app") or "", kwargs.get("ref") or "", kwargs.get("text") or "")
    if command == "wait":
        return wait(config, app=kwargs.get("app"), ref=kwargs.get("ref"),
                    text=kwargs.get("text"), wait_ms=kwargs.get("wait_ms"),
                    predicate=kwargs.get("predicate"), value=kwargs.get("value"),
                    timeout_ms=kwargs.get("timeout_ms") or 5000)
    return {"version": VERSION, "ok": False, "command": command,
            "error": {"code": "COMMAND_NOT_SUPPORTED", "message": "comando não suportado no AT-SPI"},
            "policy": {"backend": "atspi", "external_validation": False}}
