# -*- coding: utf-8 -*-
"""
OpenCode Agent SDK (SPEC-935-R649) — SDK de agente FREE, local-first.

Espelha a superfície do `claude-agent-sdk` sem conta, sem cobrança e sem
CLI proprietário: transporte HTTP OpenAI-compatível (só stdlib) contra
provedores locais já verificados nesta máquina — LiteRT-LM `:9379`,
Ollama `:11434` (ambos UP em 2026-10-03), Colibri `:8090` (ponte pronta,
servidor fora do ar).

- `query(prompt, options)` — gerador sync de eventos `text/tool_use/result`
  com loop agêntico (tools locais, hooks, `max_turns`).
- `build_options(...)` — mesmo vocabulário do `ClaudeAgentOptions`.
- `@tool` + `create_local_tool_server(...)` — tools in-process, dispatch
  direto, zero IPC (export FastMCP opcional se `mcp` instalado).
- Custo marginal: R$ 0,00. Sem fallback em nuvem: sem provedor local,
  falha explícita (FREE é garantia).
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Callable, Dict, Iterator, List, Optional

SPEC_ID = "SPEC-935-R649"

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
        _TOOLS[name] = {"description": description,
                        "parameters": parameters, "fn": fn}
        fn._opencode_tool = name  # type: ignore[attr-defined]
        return fn
    return _wrap


def create_local_tool_server(name: str, version: str = "1.0.0",
                             tools: Optional[List[Callable]] = None):
    """Servidor in-process: dict executável sem `mcp` (dispatch direto)."""
    entries = {}
    for fn in tools or []:
        tname = getattr(fn, "_opencode_tool", None) or getattr(fn, "__name__", "tool")
        meta = _TOOLS.get(tname, {"description": "", "parameters": {}})
        entries[tname] = {"description": meta["description"],
                          "parameters": meta["parameters"], "fn": fn}
    server: Dict[str, Any] = {"type": "local", "name": name,
                              "version": version, "tools": entries}
    try:
        import mcp  # noqa: F401
        server["fastmcp_export"] = True
    except ImportError:
        server["fastmcp_export"] = False
    return server


def dispatch(server: Dict[str, Any], tool_name: str, args: Dict[str, Any]) -> Any:
    """Executa uma tool do servidor in-process (síncrono)."""
    try:
        fn = server["tools"][tool_name]["fn"]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"tool desconhecida: {tool_name}") from exc
    return fn(args or {})


def build_options(
    prompt: str,
    system_prompt: Optional[str] = None,
    allowed_tools: Optional[List[str]] = None,
    disallowed_tools: Optional[List[str]] = None,
    max_turns: int = 3,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    permission_mode: Optional[str] = None,
    hooks: Optional[Dict[str, List[Callable]]] = None,
    timeout: int = 120,
) -> Dict[str, Any]:
    """Monta options no vocabulário do AgentOptions (puro, sem rede)."""
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("O prompt deve ser uma string não vazia.")
    if not isinstance(max_turns, int) or max_turns < 1:
        raise ValueError("max_turns deve ser inteiro >= 1.")
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
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(
            url, data=data, method=method,
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.load(resp)
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
                "parameters": {"type": "object",
                               "properties": meta["parameters"] or {},
                               "additionalProperties": True},
            },
        })
    return specs


def _hooks_deny(hooks: Dict[str, List[Callable]], tool_name: str,
                args: Dict[str, Any]) -> Optional[str]:
    """Roda hooks PreToolUse; retorna motivo do deny ou None.

    Aceita lambdas legadas E `HookMatcher` do `hooks/engine.py` (via chave
    "matchers"): primeiro deny vence, exceção nega (fail-closed, R653).
    """
    for fn in (hooks or {}).get("PreToolUse", []):
        # HookMatcher do Core tem .matches(); lambdas vão direto ao veredito.
        if hasattr(fn, "matches") and hasattr(fn, "hooks"):
            if not fn.matches(tool_name):
                continue
            fns = list(fn.hooks)
        else:
            fns = [fn]
        for hook in fns:
            try:
                try:
                    verdict = hook(tool_name, args, {})
                except TypeError:
                    verdict = hook(tool_name, args)
            except Exception as exc:  # noqa: BLE001 - fail-closed
                return f"hook falhou: {exc}"
            if verdict is False:
                return "negado pelo hook"
            if isinstance(verdict, dict):
                if verdict.get("permissionDecision") == "deny":
                    return str(verdict.get("permissionDecisionReason", "negado pelo hook"))
                if verdict.get("deny"):
                    return str(verdict.get("reason", "negado pelo hook"))
    return None


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
    """Gerador de eventos do loop agêntico FREE (text/tool_use/result).

    Resolve provedor (arg > detect), chama chat, executa tools permitidas
    localmente, respeita hooks/deny, até `max_turns`.
    """
    opts = dict(options or {})
    if prompt and "prompt" not in opts:
        opts["prompt"] = prompt
    if not str(opts.get("prompt", "")).strip():
        yield {"type": "error", "error": "prompt vazio"}
        return
    detected = None if opts.get("base_url") else detect_provider()
    base_url = opts.get("base_url") or (detected or {}).get("base_url", "")
    model = opts.get("model") or (detected or {}).get("model", "")
    if not base_url:
        yield {"type": "error",
               "error": "nenhum provedor local saudável (LiteRT-LM/Ollama/Colibri)"}
        return
    if not model:
        for _prov in PROVIDERS:
            if _prov["base_url"] == base_url:
                model = _prov["default_model"]
    allowed = list(opts.get("allowed_tools") or [])
    disallowed = set(opts.get("disallowed_tools") or [])
    hooks = opts.get("hooks") or {}
    max_turns = int(opts.get("max_turns") or 3)
    timeout = int(opts.get("timeout") or 120)
    messages: List[dict] = []
    if opts.get("system_prompt"):
        messages.append({"role": "system", "content": opts["system_prompt"]})
    messages.append({"role": "user", "content": opts["prompt"]})
    tools = _openai_tools(allowed)

    for _ in range(max_turns):
        answer = chat_once(messages, str(model), str(base_url), tools or None, timeout)
        if not answer.get("ok"):
            yield {"type": "error", "error": str(answer.get("error"))}
            return
        if answer.get("content"):
            yield {"type": "text", "text": answer["content"]}
        calls = answer.get("tool_calls") or []
        if not calls:
            yield {"type": "result", "finish": "stop"}
            return
        for call in calls:
            fn = (call.get("function") or {})
            name = fn.get("name", "")
            try:
                args = json.loads(fn.get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}
            if name not in allowed or name in disallowed or name not in _TOOLS:
                yield {"type": "tool_denied", "tool": name,
                       "reason": "fora da allowlist"}
                messages.append({"role": "tool", "tool_call_id": call.get("id", ""),
                                 "content": "negado: fora da allowlist"})
                continue
            denied = _hooks_deny(hooks, name, args)
            if denied:
                yield {"type": "tool_denied", "tool": name, "reason": denied}
                messages.append({"role": "tool", "tool_call_id": call.get("id", ""),
                                 "content": f"negado pelo hook: {denied}"})
                continue
            try:
                output = _TOOLS[name]["fn"](args)
            except Exception as exc:  # noqa: BLE001 - erro da tool vira evento
                output = f"erro na tool: {exc}"
            yield {"type": "tool_use", "tool": name, "output": output}
            messages.append({"role": "tool", "tool_call_id": call.get("id", ""),
                             "content": str(output)[:4000]})
    yield {"type": "result", "finish": "max_turns"}


def doctor_check() -> Dict[str, str]:
    """DoctorCheck (pass com ≥1 provedor saudável; nunca fail)."""
    prov = detect_provider()
    if prov:
        return {
            "name": "opencode-agent-sdk",
            "status": "pass",
            "detail": f"SDK livre pronto via {prov['id']} ({prov.get('model')}). SPEC-935-R649.",
        }
    return {
        "name": "opencode-agent-sdk",
        "status": "warn",
        "detail": "Nenhum provedor local saudável (LiteRT-LM :9379, Ollama :11434, Colibri :8090). SPEC-935-R649.",
    }


def install_instructions() -> str:
    """Como subir um provedor local gratuito."""
    return (
        "OpenCode Agent SDK — custo R$ 0,00 (inferência local, sem conta):\n"
        "  LiteRT-LM (on-device): verificado via doctor do Core (litert_lm)\n"
        "  Ollama: ollama serve  &  ollama pull gemma4:e2b-tuned\n"
        "  Colibri: binário OLMoE (ver doctor colibri)\n"
        "\n"
        "Uso no Core:\n"
        "  /opencode-sdk status\n"
        "  /opencode-sdk query --prompt '...' [--model M] [--max-turns 3]\n"
        "Override: OPENCODE_SDK_BASE_URL (+ OPENCODE_SDK_MODEL)."
    )


def _format_status() -> str:
    prov = detect_provider()
    return json.dumps(
        {"especificacao": SPEC_ID, "custo": "R$ 0,00",
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
        prompt = model = base = system = ""
        max_turns = 3
        idx = 0
        while idx < len(rest):
            tok = rest[idx]
            if tok in ("--prompt", "--model", "--base-url", "--max-turns", "--system") and idx + 1 < len(rest):
                key = {"--prompt": "prompt", "--model": "model", "--base-url": "base",
                       "--max-turns": "max_turns", "--system": "system"}[tok]
                val = rest[idx + 1]
                if key == "prompt": prompt = val
                elif key == "model": model = val
                elif key == "base": base = val
                elif key == "system": system = val
                else:
                    try: max_turns = int(val)
                    except ValueError:
                        print("max-turns deve ser inteiro."); return 2
                idx += 2
                continue
            idx += 1
        if not prompt.strip():
            print("Uso: query --prompt '...' [--max-turns N]")
            return 2
        opts = build_options(prompt, system_prompt=system or None,
                             max_turns=max_turns,
                             model=model or None, base_url=base or None)
        for ev in query(prompt, opts):
            print(json.dumps(ev, ensure_ascii=False)[:1000])
        return 0
    print(f"Comando desconhecido: {command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
