# -*- coding: utf-8 -*-
"""
OpenCode Agent SDK (SPEC-935-R649/R659) — loop local por padrão.

Oferece query, opções, ferramentas em processo e hooks do Core sobre HTTP
OpenAI-compatível. A sondagem /models constata disponibilidade do endpoint;
inferência e tool calling exigem execução separada. jsonschema valida
argumentos de ferramentas antes dos handlers.

- `query(prompt, options)` — gerador sync de eventos `text/tool_use/result`
  com loop agêntico (tools locais, hooks, `max_turns`).
- `build_options(...)` — mesmo vocabulário do `ClaudeAgentOptions`.
- `@tool` + `create_local_tool_server(...)` — tools in-process, dispatch
  direto, zero IPC; não exporta um servidor MCP.
- Sem fallback automático em nuvem. Overrides de base_url são explícitos e
  suas condições de custo não são avaliadas por este módulo.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from copy import deepcopy
from typing import Any, Callable, Dict, Iterator, List, Optional

SPEC_ID = "SPEC-935-R649"
MAX_TURNS = 100

PROVIDERS = (
    {"id": "litert-lm", "base_url": "http://localhost:9379/v1",
     "default_model": "litert-community/gemma-4-E2B-it-litert-lm"},
    {"id": "ollama", "base_url": "http://localhost:11434/v1",
     "default_model": "gemma4:e2b-tuned"},
    {"id": "colibri", "base_url": "http://localhost:8090/v1",
     "default_model": "olmoe-1b-7b"},
)

_NO_KEY = "sk-no-key-required"
_TOOLS: Dict[str, Dict[str, Any]] = {}


def tool(name: str, description: str, parameters: Dict[str, Any]):
    """Registra uma função sync como tool local (decorador)."""
    def _wrap(fn: Callable[[Dict[str, Any]], Any]):
        meta = {"description": description, "parameters": deepcopy(parameters), "fn": fn}
        _TOOLS[name] = meta
        fn._opencode_tool = name  # type: ignore[attr-defined]
        fn._opencode_metadata = meta  # type: ignore[attr-defined]
        return fn
    return _wrap


def create_local_tool_server(name: str, version: str = "1.0.0",
                             tools: Optional[List[Callable]] = None):
    """Servidor in-process: dict executável sem `mcp` (dispatch direto)."""
    entries = {}
    for fn in tools or []:
        tname = getattr(fn, "_opencode_tool", None) or getattr(fn, "__name__", "tool")
        meta = getattr(fn, "_opencode_metadata", None) or _TOOLS.get(
            tname, {"description": "", "parameters": {}})
        entries[tname] = {"description": meta["description"],
                          "parameters": deepcopy(meta["parameters"]), "fn": fn}
    server: Dict[str, Any] = {"type": "local", "name": name,
                              "version": version, "tools": entries,
                              "fastmcp_export": False}
    try:
        import mcp  # noqa: F401
        server["mcp_available"] = True
    except ImportError:
        server["mcp_available"] = False
    return server


def dispatch(server: Dict[str, Any], tool_name: str, args: Dict[str, Any]) -> Any:
    """Executa uma tool do servidor in-process (síncrono)."""
    try:
        entry = server["tools"][tool_name]
        fn = entry["fn"]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"tool desconhecida: {tool_name}") from exc
    from integrations.mcp_validation import validate_arguments
    validation = validate_arguments(tool_name, args, _tool_schema(entry["parameters"]))
    if not validation["valid"]:
        raise ValueError("argumentos inválidos: " + "; ".join(validation["errors"]))
    return fn(validation["args"])


def build_options(
    prompt: str,
    system_prompt: Optional[str] = None,
    allowed_tools: Optional[List[str]] = None,
    disallowed_tools: Optional[List[str]] = None,
    max_turns: int = 3,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    permission_mode: Optional[str] = None,
    hooks: Optional[Dict[str, List[Any]]] = None,
    timeout: int = 120,
) -> Dict[str, Any]:
    """Monta options no vocabulário do AgentOptions (puro, sem rede)."""
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("O prompt deve ser uma string não vazia.")
    if type(max_turns) is not int or not 1 <= max_turns <= MAX_TURNS:
        raise ValueError(f"max_turns deve ser inteiro entre 1 e {MAX_TURNS}.")
    if type(timeout) is not int or not 1 <= timeout <= 3600:
        raise ValueError("timeout deve ser inteiro entre 1 e 3600 segundos.")
    for key, names in (("allowed_tools", allowed_tools), ("disallowed_tools", disallowed_tools)):
        if names is not None and (not isinstance(names, list) or any(
                not isinstance(name, str) or not name for name in names)):
            raise ValueError(f"{key} deve ser uma lista de nomes de ferramentas.")
    if hooks is not None:
        from hooks.engine import EVENTS
        if not isinstance(hooks, dict) or any(
                event not in (*EVENTS, "matchers") or not isinstance(entries, list)
                for event, entries in hooks.items()):
            raise ValueError("hooks deve mapear eventos conhecidos a listas de callbacks/matchers.")
    return {
        "prompt": prompt, "system_prompt": system_prompt,
        "allowed_tools": list(allowed_tools or []),
        "disallowed_tools": list(disallowed_tools or []),
        "max_turns": max_turns, "model": model, "base_url": base_url,
        "permission_mode": permission_mode or "default",
        "hooks": hooks or {}, "timeout": timeout,
    }


def _http_json(method: str, url: str, payload: Optional[dict] = None,
               timeout: int = 5) -> Optional[Any]:
    """GET/POST JSON com urllib; None em qualquer falha (nunca lança)."""
    try:
        deadline = time.monotonic() + timeout
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(
            url, data=data, method=method,
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if not hasattr(resp, "read1"):
                # Compatibilidade com transports/file-like legados; respostas
                # HTTP de urllib possuem read1 e usam o prazo total abaixo.
                return json.load(resp)
            chunks = []
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("prazo total HTTP excedido")
                sock = getattr(getattr(getattr(resp, "fp", None), "raw", None), "_sock", None)
                if sock is not None:
                    sock.settimeout(remaining)
                chunk = resp.read1(65536)
                if not chunk:
                    return json.loads(b"".join(chunks))
                chunks.append(chunk)
    except Exception:
        return None


def provider_healthy(base_url: str, timeout: int = 5) -> bool:
    """True se `{base}/models` responde (sondagem leve, sem inferência)."""
    got = _http_json("GET", base_url.rstrip("/") + "/models", timeout=timeout)
    return isinstance(got, dict) and isinstance(got.get("data"), list)


def detect_provider(timeout: int = 5) -> Optional[Dict[str, str]]:
    """Primeiro provedor saudável: env > LiteRT-LM > Ollama > Colibri."""
    env_base = os.environ.get("OPENCODE_SDK_BASE_URL")
    if env_base:
        if provider_healthy(env_base, timeout):
            return {"id": "env", "base_url": env_base,
                    "model": os.environ.get("OPENCODE_SDK_MODEL", "")}
        return None
    for prov in PROVIDERS:
        if provider_healthy(prov["base_url"], timeout):
            return {"id": prov["id"], "base_url": prov["base_url"],
                    "model": prov["default_model"]}
    return None


def _tool_schema(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Aceita JSON Schema completo ou mapa legado de propriedades (R659)."""
    if not isinstance(parameters, dict):
        raise ValueError("schema de ferramenta deve ser objeto")
    if (isinstance(parameters.get("type"), str) or
            any(key in parameters for key in ("$schema", "$ref", "properties", "allOf", "anyOf", "oneOf"))):
        return deepcopy(parameters)
    return {"type": "object", "properties": deepcopy(parameters),
            "additionalProperties": True}


def _openai_tools(allowed: List[str]) -> List[dict]:
    """Converte tools registradas no schema `tools` do chat completions."""
    specs = []
    for name in allowed:
        meta = _TOOLS.get(name)
        if not meta:
            continue
        specs.append({
            "type": "function",
            "function": {
                "name": name, "description": meta["description"],
                "parameters": _tool_schema(meta["parameters"]),
            },
        })
    return specs


def _event_hooks(hooks: Dict[str, List[Any]], event: str, tool_name: str = "",
                 args: Optional[dict] = None, context: Optional[dict] = None) -> Dict[str, Any]:
    """Normaliza callbacks e matchers para a engine única do Core."""
    from hooks.engine import HookMatcher, run_hooks
    entries = list((hooks or {}).get(event, []))
    if event == "PreToolUse":
        entries.extend((hooks or {}).get("matchers", []))
    matchers = [entry if isinstance(entry, HookMatcher) else HookMatcher("*", [entry])
                for entry in entries]
    return run_hooks(event, tool_name, args, matchers, context)


def _hooks_deny(hooks: Dict[str, List[Any]], tool_name: str,
                args: Dict[str, Any]) -> Optional[str]:
    """Adaptador legado; a engine unificada decide PreToolUse."""
    verdict = _event_hooks(hooks, "PreToolUse", tool_name, args)
    return None if verdict["allow"] else verdict["reason"]


def chat_once(messages: List[dict], model: str, base_url: str,
              tools: Optional[List[dict]] = None,
              timeout: int = 120) -> Dict[str, Any]:
    """Uma chamada `/chat/completions`; dict normalizado (nunca lança)."""
    payload: Dict[str, Any] = {"model": model, "messages": messages}
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    got = _http_json("POST", base_url.rstrip("/") + "/chat/completions",
                     payload, timeout)
    try:
        msg = got["choices"][0]["message"]  # type: ignore[index]
        return {"ok": True, "content": msg.get("content") or "",
                "tool_calls": msg.get("tool_calls") or []}
    except (TypeError, KeyError, IndexError):
        return {"ok": False, "error": "resposta inválida do provedor",
                "content": "", "tool_calls": []}


def query(prompt: str, options: Optional[Dict[str, Any]] = None
          ) -> Iterator[Dict[str, Any]]:
    """Loop agêntico com lifecycle e validação antes dos efeitos (R659)."""
    try:
        raw = dict(options or {})
        opts = build_options(
            raw.get("prompt", prompt), system_prompt=raw.get("system_prompt"),
            allowed_tools=raw.get("allowed_tools"), disallowed_tools=raw.get("disallowed_tools"),
            max_turns=raw.get("max_turns", 3), model=raw.get("model"),
            base_url=raw.get("base_url"), permission_mode=raw.get("permission_mode"),
            hooks=raw.get("hooks"), timeout=raw.get("timeout", 120),
        )
    except (ValueError, TypeError) as exc:
        yield {"type": "error", "error": str(exc)}
        return
    hooks = opts["hooks"]
    context = {"prompt": opts["prompt"], "model": opts["model"], "base_url": opts["base_url"]}
    finish = "cancelled"
    try:
        start = _event_hooks(hooks, "SessionStart", context=context)
        if not start["allow"]:
            finish = "error"
            yield {"type": "error", "error": "SessionStart: " + start["reason"]}
        else:
            finish = yield from _query_loop(opts, context)
    except Exception as exc:  # noqa: BLE001 - explicitar falhas e encerrar lifecycle
        finish = "error"
        yield {"type": "error", "error": f"falha no SDK: {exc}"}
    finally:
        # Também executa em close()/GeneratorExit; nunca yield no finally.
        end = _event_hooks(hooks, "SessionEnd", context={**context, "finish": finish})
    if not end["allow"]:
        yield {"type": "error", "error": "SessionEnd: " + end["reason"]}
        return
    if finish in ("stop", "max_turns"):
        yield {"type": "result", "finish": finish}


def _query_loop(opts: Dict[str, Any], context: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
    """Produz eventos e devolve finish; query garante SessionEnd."""
    from integrations.mcp_validation import validate_arguments
    detected = None if opts.get("base_url") else detect_provider()
    base_url = opts.get("base_url") or (detected or {}).get("base_url", "")
    model = opts.get("model") or (detected or {}).get("model", "")
    if not base_url:
        yield {"type": "error",
               "error": "nenhum provedor local saudável (LiteRT-LM/Ollama/Colibri)"}
        return "error"
    if not model:
        for _prov in PROVIDERS:
            if _prov["base_url"] == base_url:
                model = _prov["default_model"]
    if not model:
        yield {"type": "error", "error": "modelo não definido para o provedor"}
        return "error"
    disallowed = set(opts.get("disallowed_tools") or [])
    allowed = [name for name in dict.fromkeys(opts.get("allowed_tools") or [])
               if name not in disallowed]
    hooks = opts.get("hooks") or {}
    max_turns = opts["max_turns"]
    timeout = opts["timeout"]
    context.update(model=model, base_url=base_url)
    messages: List[dict] = []
    if opts.get("system_prompt"):
        messages.append({"role": "system", "content": opts["system_prompt"]})
    messages.append({"role": "user", "content": opts["prompt"]})
    tools = _openai_tools(allowed)

    for turn in range(max_turns):
        answer = chat_once(messages, str(model), str(base_url), tools or None, timeout)
        if not answer.get("ok"):
            yield {"type": "error", "error": str(answer.get("error"))}
            return "error"
        if answer.get("content"):
            yield {"type": "text", "text": answer["content"]}
        calls = answer.get("tool_calls") or []
        if not calls:
            return "stop"
        if not isinstance(calls, list) or any(
                not isinstance(call, dict) or call.get("type") != "function" or
                not isinstance(call.get("id"), str) or not call["id"] or
                not isinstance(call.get("function"), dict) or
                not isinstance(call["function"].get("name"), str) or
                not isinstance(call["function"].get("arguments"), str)
                for call in calls):
            yield {"type": "error", "error": "tool_calls inválidos do provedor"}
            return "error"
        if len({call["id"] for call in calls}) != len(calls):
            yield {"type": "error", "error": "tool_calls com IDs duplicados"}
            return "error"
        messages.append({"role": "assistant", "content": answer.get("content") or None,
                         "tool_calls": calls})
        for call in calls:
            fn = (call.get("function") or {})
            name = fn.get("name", "")
            denied = "fora da allowlist" if name not in allowed or name not in _TOOLS else None
            args: Any = {}
            if denied is None:
                try:
                    args = json.loads(fn["arguments"])
                except (json.JSONDecodeError, TypeError):
                    denied = "argumentos inválidos: JSON malformado"
            if denied is None:
                validation = validate_arguments(name, args, _tool_schema(_TOOLS[name]["parameters"]))
                if not validation["valid"]:
                    denied = "argumentos inválidos: " + "; ".join(validation["errors"])
                else:
                    args = validation["args"]
            tool_context = {**context, "turn": turn + 1, "tool_call_id": call["id"]}
            if denied is None:
                pre = _event_hooks(hooks, "PreToolUse", name, args, tool_context)
                if not pre["allow"]:
                    denied = pre["reason"]
                else:
                    # Hooks locais podem alterar o dict; o contrato permanece
                    # válido imediatamente antes do efeito da ferramenta.
                    validation = validate_arguments(name, args, _tool_schema(_TOOLS[name]["parameters"]))
                    if not validation["valid"]:
                        denied = "argumentos inválidos após hook: " + "; ".join(validation["errors"])
            if denied:
                yield {"type": "tool_denied", "tool": name, "reason": denied}
                messages.append({"role": "tool", "tool_call_id": call["id"],
                                 "content": json.dumps({"error": denied}, ensure_ascii=False)})
                continue
            tool_failed = False
            try:
                output = _TOOLS[name]["fn"](args)
            except Exception as exc:  # noqa: BLE001 - erro da tool vira evento
                output = {"error": f"erro na tool: {exc}"}
                tool_failed = True
            messages.append({"role": "tool", "tool_call_id": call["id"],
                             "content": json.dumps(output, ensure_ascii=False, default=str)[:4000]})
            post = _event_hooks(hooks, "PostToolUse", name, args,
                                {**tool_context, "output": output, "is_error": tool_failed})
            # O pós-hook antecede yield: close() do consumidor não o omite
            # depois de a ferramenta já ter produzido um efeito.
            yield {"type": "tool_use", "tool": name, "output": output,
                   **({"is_error": True} if tool_failed else {})}
            if not post["allow"]:
                yield {"type": "error", "error": "PostToolUse: " + post["reason"]}
                return "error"
    return "max_turns"


def doctor_check() -> Dict[str, str]:
    """DoctorCheck (pass com ≥1 provedor saudável; nunca fail)."""
    prov = detect_provider()
    if prov:
        return {
            "name": "opencode-agent-sdk",
            "status": "pass",
            "detail": f"Endpoint /models acessível via {prov['id']} ({prov.get('model')}); inferência não testada. SPEC-935-R649.",
        }
    return {
        "name": "opencode-agent-sdk",
        "status": "warn",
        "detail": "Nenhum provedor local saudável (LiteRT-LM :9379, Ollama :11434, Colibri :8090). SPEC-935-R649.",
    }


def install_instructions() -> str:
    """Como subir um provedor local gratuito."""
    return (
        "OpenCode Agent SDK — inferência local padrão, custo marginal R$ 0,00:\n"
        "  LiteRT-LM (on-device): disponibilidade consultada pelo doctor do Core\n"
        "  Ollama: ollama serve  &  ollama pull gemma4:e2b-tuned\n"
        "  Colibri: binário OLMoE (ver doctor colibri)\n"
        "\n"
        "Uso no Core:\n"
        "  /opencode-sdk status\n"
        "  /opencode-sdk query --prompt '...' [--model M] [--max-turns 3]\n"
        "Override: OPENCODE_SDK_BASE_URL (+ OPENCODE_SDK_MODEL); custo do endpoint não avaliado."
    )


def _format_status() -> str:
    prov = detect_provider()
    return json.dumps(
        {"especificacao": SPEC_ID, "custo": "padrão local; override não avaliado",
         "provedor": prov, "licenca": "livre (Core)",
         "transporte": "HTTP OpenAI-compativel (stdlib)"},
        ensure_ascii=False, indent=2,
    )


def main(argv: Optional[List[str]] = None) -> int:
    import sys as _sys
    argv = list(_sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"--help", "-h", "help"}:
        print(
            "Uso: python3 -m integrations.opencode_agent_sdk <status|doctor|install|query|tools> [args...]\n"
            "  query --prompt '...' [--model M] [--base-url U] [--max-turns N] [--system S]"
        )
        return 0
    command, *rest = argv
    if command == "status":
        print(_format_status())
        return 0
    if command == "doctor":
        check = doctor_check()
        print(f"{check['name']}: {check['status']} — {check['detail']}")
        return 0 if check["status"] == "pass" else 1
    if command == "install":
        print(install_instructions())
        return 0
    if command == "tools":
        print(json.dumps(
            {n: {"description": m["description"]} for n, m in _TOOLS.items()},
            ensure_ascii=False, indent=2))
        return 0
    if command == "query":
        import argparse
        parser = argparse.ArgumentParser(prog="opencode-sdk query")
        parser.add_argument("--prompt", required=True)
        parser.add_argument("--model")
        parser.add_argument("--base-url")
        parser.add_argument("--max-turns", type=int, default=3)
        parser.add_argument("--system")
        try:
            parsed = parser.parse_args(rest)
        except SystemExit as exc:
            return int(exc.code)
        try:
            opts = build_options(parsed.prompt, system_prompt=parsed.system,
                                 max_turns=parsed.max_turns,
                                 model=parsed.model, base_url=parsed.base_url)
        except ValueError as exc:
            print(str(exc))
            return 2
        exit_code = 0
        for ev in query(parsed.prompt, opts):
            print(json.dumps(ev, ensure_ascii=False)[:1000])
            if ev["type"] == "error" or ev.get("is_error") or ev.get("finish") == "max_turns":
                exit_code = 1
        return exit_code
    print(f"Comando desconhecido: {command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
