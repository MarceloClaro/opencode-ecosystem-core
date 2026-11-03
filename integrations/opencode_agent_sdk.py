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
import re
import time
import uuid
import urllib.error
import urllib.parse
import urllib.request
from copy import deepcopy
from typing import Any, Callable, Dict, Iterator, List, Optional

SPEC_ID = "SPEC-935-R649"
MAX_TURNS = 100

PROVIDERS = (
    {"id": "litert-lm", "base_url": "http://localhost:9379/v1",
     "default_model": "litert-community/gemma-4-E2B-it-litert-lm",
     "context_window": 20480},
    {"id": "ollama", "base_url": "http://localhost:11434/v1",
     "default_model": "gemma4:e2b-tuned", "context_window": 24576},
    {"id": "colibri", "base_url": "http://localhost:8090/v1",
     "default_model": "olmoe-1b-7b"},
)

# Limites declarados pelo catálogo do Core; não são sondagem do Modelfile ativo.
MODEL_CONTEXT_WINDOWS = {
    "gemma4:e2b-tuned": 24576,
    "gemma4:e4b-tuned": 24576,
    "llama3.2": 32768,
    "litert-community/gemma-4-E2B-it-litert-lm": 20480,
    "litert-community/gemma-4-E4B-it-litert-lm": 20480,
    "litert-community/gemma-4-12B-it-litert-lm": 20480,
}
MAX_CONTEXT_WINDOW = 2_000_000
MAX_OUTPUT_TOKENS = 65_536
MAX_CONTEXT_SAFETY_TOKENS = 8_192

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
    context_window: Optional[int] = None,
    max_output_tokens: Optional[int] = None,
    context_safety_tokens: int = 256,
) -> Dict[str, Any]:
    """Monta options no vocabulário do AgentOptions (puro, sem rede)."""
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("O prompt deve ser uma string não vazia.")
    if type(max_turns) is not int or not 1 <= max_turns <= MAX_TURNS:
        raise ValueError(f"max_turns deve ser inteiro entre 1 e {MAX_TURNS}.")
    if type(timeout) is not int or not 1 <= timeout <= 3600:
        raise ValueError("timeout deve ser inteiro entre 1 e 3600 segundos.")
    if context_window is not None and (type(context_window) is not int or
                                       not 256 <= context_window <= MAX_CONTEXT_WINDOW):
        raise ValueError(f"context_window deve ser inteiro entre 256 e {MAX_CONTEXT_WINDOW}.")
    if max_output_tokens is not None and (type(max_output_tokens) is not int or
                                           not 1 <= max_output_tokens <= MAX_OUTPUT_TOKENS):
        raise ValueError(f"max_output_tokens deve ser inteiro entre 1 e {MAX_OUTPUT_TOKENS}.")
    if type(context_safety_tokens) is not int or not 0 <= context_safety_tokens <= MAX_CONTEXT_SAFETY_TOKENS:
        raise ValueError(f"context_safety_tokens deve ser inteiro entre 0 e {MAX_CONTEXT_SAFETY_TOKENS}.")
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
        "context_window": context_window, "max_output_tokens": max_output_tokens,
        "context_safety_tokens": context_safety_tokens,
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


def _estimate_tokens(text: str) -> int:
    """Estimativa deliberadamente conservadora por bytes; não substitui tokenizer."""
    raw = text.encode("utf-8", errors="replace")
    return max(1, (len(raw) + 2) // 3) if raw else 0


def _classify_http_error(status: int, message: str) -> str:
    detail = message.lower()
    if status == 413 or any(marker in detail for marker in (
            "context length", "context_length", "too many tokens", "prompt is too long",
            "context window", "context exceeded", "maximum context", "input is too long",
            "input length", "num_ctx", "exceeds the model's maximum")):
        return "context_window_exceeded"
    if status == 429:
        if any(marker in detail for marker in ("quota", "resource_exhausted", "billing", "token_count")):
            return "quota_exceeded"
        return "rate_limited"
    if status in {401, 403}:
        return "authentication_failed"
    if status == 404:
        return "model_or_endpoint_not_found"
    if status in {408, 504}:
        return "request_timeout"
    if status >= 500:
        return "provider_unavailable"
    return "provider_rejected_request"


def _retry_after(headers, message: str = "") -> Optional[Any]:
    value = headers.get("Retry-After") if headers is not None else None
    if value is not None:
        try:
            number = float(value)
            return int(number) if number.is_integer() else number
        except (TypeError, ValueError):
            # HTTP also permits an HTTP-date. Preserve it rather than inventing a delay.
            return str(value)[:80]
    match = re.search(r"retry\s+(?:after|in)\s+([0-9]+(?:\.[0-9]+)?)\s*(?:s|sec|seconds?)\b",
                      message, re.IGNORECASE)
    return float(match.group(1)) if match else None


def _http_json_detailed(method: str, url: str, payload: Optional[dict], timeout: int):
    """HTTP JSON with typed operational failure; never returns raw prompts in errors."""
    deadline = time.monotonic() + timeout
    data = json.dumps(payload, ensure_ascii=False).encode() if payload is not None else None
    request = urllib.request.Request(url, data=data, method=method,
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if not hasattr(response, "read1"):
                body = response.read()
            else:
                chunks = []
                while True:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise TimeoutError("prazo total HTTP excedido")
                    sock = getattr(getattr(getattr(response, "fp", None), "raw", None), "_sock", None)
                    if sock is not None:
                        sock.settimeout(remaining)
                    chunk = response.read1(65536)
                    if not chunk:
                        body = b"".join(chunks)
                        break
                    chunks.append(chunk)
            try:
                decoded = json.loads(body)
            except (UnicodeError, json.JSONDecodeError):
                return {"ok": False, "code": "invalid_provider_response",
                    "message": "O endpoint retornou uma resposta que não é JSON válido.",
                    "http_status": getattr(response, "status", None)}
            return {"ok": True, "data": decoded, "http_status": getattr(response, "status", 200)}
    except urllib.error.HTTPError as exc:
        try:
            raw = exc.read(4096)
            decoded = json.loads(raw) if raw else {}
        except (OSError, UnicodeError, json.JSONDecodeError):
            decoded = {}
        error_value = decoded.get("error", {}) if isinstance(decoded, dict) else {}
        provider_message = (error_value.get("message", "") if isinstance(error_value, dict)
                            else error_value if isinstance(error_value, str) else "")
        if not provider_message and isinstance(decoded, dict) and isinstance(decoded.get("message"), str):
            provider_message = decoded["message"]
        if not isinstance(provider_message, str):
            provider_message = ""
        code = _classify_http_error(exc.code, provider_message)
        messages = {
            "context_window_exceeded": "O contexto excede o limite reportado pelo provedor. Reduza/estruture a entrada ou configure uma janela maior explicitamente; nenhum texto foi truncado.",
            "quota_exceeded": "Quota do provedor excedida. Aguarde Retry-After ou verifique tier/billing; não houve retry nem troca automática de modelo.",
            "rate_limited": "O provedor aplicou rate limit. Aguarde Retry-After; não houve retry automático.",
            "authentication_failed": "Autenticação recusada pelo endpoint local/provider.",
            "model_or_endpoint_not_found": "Modelo ou endpoint não encontrado no provider selecionado.",
            "request_timeout": "Prazo da requisição excedido; a chamada não foi repetida.",
            "provider_unavailable": "O provider reportou indisponibilidade; a chamada não foi repetida.",
            "provider_rejected_request": "O provider recusou a solicitação; confira o schema e os limites informados.",
        }
        return {"ok": False, "code": code, "message": messages[code],
            "http_status": exc.code, "retry_after_seconds": _retry_after(exc.headers, provider_message)}
    except (TimeoutError, urllib.error.URLError, OSError) as exc:
        timeout_error = isinstance(exc, TimeoutError) or isinstance(getattr(exc, "reason", None), TimeoutError)
        return {"ok": False, "code": "request_timeout" if timeout_error else "provider_unavailable",
            "message": "O provider local não respondeu dentro do prazo." if timeout_error else
                "Não foi possível conectar ao provider local configurado.", "http_status": None}
    except Exception as exc:
        return {"ok": False, "code": "transport_error",
            "message": f"Falha de transporte ({type(exc).__name__}); conteúdo do pedido omitido.",
            "http_status": None}


def _probe_ollama_context(base_url: str, model: str, timeout: int = 5) -> dict:
    """Consulta `/api/show` apenas em Ollama loopback; não executa inferência."""
    parsed = urllib.parse.urlsplit(base_url)
    if parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        return {"ok": False, "code": "context_probe_not_local"}
    origin = f"{parsed.scheme or 'http'}://{parsed.netloc}"
    response = _http_json_detailed("POST", origin + "/api/show",
        {"model": model, "verbose": False}, min(timeout, 10))
    if not response.get("ok"):
        return {"ok": False, "code": response.get("code", "context_probe_failed"),
                "http_status": response.get("http_status"),
                "retry_after_seconds": response.get("retry_after_seconds")}
    data = response.get("data")
    modelfile = data.get("modelfile", "") if isinstance(data, dict) else ""
    if not isinstance(modelfile, str):
        modelfile = ""
    match = re.search(r"(?im)^\s*PARAMETER\s+num_ctx\s+(\d+)\s*$", modelfile)
    if match:
        return {"ok": True, "context_window": int(match.group(1)),
                "source": "ollama_api_show_modelfile_num_ctx"}
    # Ollama's Modelfile reference documents num_ctx default=2048. This value
    # is an API/Modelfile default, not a separate hardware/runtime measurement.
    return {"ok": True, "context_window": 2048,
            "source": "ollama_api_show_documented_default_num_ctx"}


def provider_healthy(base_url: str, timeout: int = 5) -> bool:
    """True se `{base}/models` responde (sondagem leve, sem inferência)."""
    got = _http_json("GET", base_url.rstrip("/") + "/models", timeout=timeout)
    return isinstance(got, dict) and isinstance(got.get("data"), list)


def detect_provider(timeout: int = 5) -> Optional[Dict[str, Any]]:
    """Primeiro provedor saudável: env > LiteRT-LM > Ollama > Colibri."""
    env_base = os.environ.get("OPENCODE_SDK_BASE_URL")
    if env_base:
        if provider_healthy(env_base, timeout):
            return {"id": "env", "base_url": env_base,
                    "model": os.environ.get("OPENCODE_SDK_MODEL", ""),
                    "context_window": None}
        return None
    for prov in PROVIDERS:
        if provider_healthy(prov["base_url"], timeout):
                return {"id": prov["id"], "base_url": prov["base_url"],
                        "model": prov["default_model"],
                        "context_window": prov.get("context_window")}
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


def _valid_tool_calls(calls: Any) -> bool:
    """Valida a estrutura inteira antes de publicar sucesso ou executar tools."""
    return isinstance(calls, list) and all(
        isinstance(call, dict) and call.get("type") == "function" and
        isinstance(call.get("id"), str) and bool(call["id"]) and
        isinstance(call.get("function"), dict) and
        isinstance(call["function"].get("name"), str) and
        bool(call["function"]["name"]) and
        isinstance(call["function"].get("arguments"), str)
        for call in calls
    ) and len({call["id"] for call in calls}) == len(calls)


def chat_once(messages: List[dict], model: str, base_url: str,
              tools: Optional[List[dict]] = None,
              timeout: int = 120,
              max_output_tokens: Optional[int] = None) -> Dict[str, Any]:
    """Uma chamada `/chat/completions`; dict normalizado (nunca lança)."""
    payload: Dict[str, Any] = {"model": model, "messages": messages}
    if max_output_tokens is not None:
        payload["max_tokens"] = max_output_tokens
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    response = _http_json_detailed("POST", base_url.rstrip("/") + "/chat/completions",
                                   payload, timeout)
    if not response.get("ok"):
        return {"ok": False, **{key: response.get(key) for key in
            ("code", "message", "http_status", "retry_after_seconds")}}
    got = response.get("data")
    choices = got.get("choices") if isinstance(got, dict) else None
    first = choices[0] if isinstance(choices, list) and choices else None
    msg = first.get("message") if isinstance(first, dict) else None
    content = msg.get("content") if isinstance(msg, dict) else None
    calls = msg.get("tool_calls") if isinstance(msg, dict) else None
    # null é permitido para mensagens assistant de tool calling; outros tipos
    # falsy (por exemplo {}) não podem ser normalizados silenciosamente para [].
    calls = [] if calls is None else calls
    if (not isinstance(msg, dict) or
            (content is not None and not isinstance(content, str)) or
            not _valid_tool_calls(calls)):
        return {"ok": False, "code": "invalid_provider_response",
                "error": "O provedor retornou choices/message/content/tool_calls inválidos.",
                "content": "", "tool_calls": []}
    return {"ok": True, "content": content or "", "tool_calls": calls,
            "usage": got.get("usage"),
            "actual_model": got.get("model") if isinstance(got.get("model"), str) else None}


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
            context_window=raw.get("context_window"),
            max_output_tokens=raw.get("max_output_tokens"),
            context_safety_tokens=raw.get("context_safety_tokens", 256),
        )
    except (ValueError, TypeError) as exc:
        yield {"type": "error", "error": str(exc)}
        return
    hooks = opts["hooks"]
    context = {"query_id": "query-" + uuid.uuid4().hex,
        "prompt": opts["prompt"], "model": opts["model"], "base_url": opts["base_url"]}
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
    provider_id = (detected or {}).get("id")
    if provider_id is None:
        provider_id = next((provider["id"] for provider in PROVIDERS
                            if provider["base_url"] == base_url), "explicit_endpoint")
    # A origem da configuração (inclusive env) não muda o tipo do endpoint.
    parsed_endpoint = urllib.parse.urlsplit(str(base_url))
    if parsed_endpoint.hostname in {"localhost", "127.0.0.1", "::1"} and parsed_endpoint.port == 11434:
        provider_id = "ollama"
    context_window = opts.get("context_window")
    context_source = "explicit_option_unverified" if context_window is not None else None
    if provider_id == "ollama":
        probe = _probe_ollama_context(str(base_url), str(model), timeout=opts["timeout"])
        if not probe.get("ok"):
            if context_window is None:
                yield {"type": "error", "code": "ollama_context_probe_failed",
                    "error": "Não foi possível confirmar o num_ctx ativo do Ollama via /api/show; confira o modelo/daemon ou passe uma janela explícita.",
                    "probe_code": probe.get("code"), "http_status": probe.get("http_status"),
                    "retry_after_seconds": probe.get("retry_after_seconds"),
                    "model": model, "provider": provider_id, "request_sent": False,
                    "context_window_verified": False,"query_id": context.get("query_id")}
                return "error"
            context_source = "operator_declared_unverified_after_probe_failure"
        else:
            runtime_context = probe["context_window"]
            if context_window is not None:
                context_window = min(context_window, runtime_context)
                context_source = "min_operator_cap_and_" + probe["source"]
            else:
                context_window = runtime_context
                context_source = probe["source"]
    elif context_window is None and detected and detected.get("context_window"):
        context_window = detected["context_window"]
        context_source = "provider_default_declared"
    elif context_window is None and model in MODEL_CONTEXT_WINDOWS:
        context_window = MODEL_CONTEXT_WINDOWS[model]
        context_source = "model_catalog_declared"
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
        estimated_input = _estimate_tokens(json.dumps(
            {"messages": messages, "tools": tools or []}, ensure_ascii=False, default=str))
        reserved_output = opts["max_output_tokens"] or 0
        budget = estimated_input + reserved_output + opts["context_safety_tokens"]
        if context_window is not None and budget > context_window:
            yield {"type": "error", "code": "context_budget_exceeded",
                "error": "A estimativa conservadora excede a janela de contexto declarada. Reduza/estruture a entrada ou configure uma janela maior explicitamente; nenhum conteúdo foi truncado.",
                "estimated_input_tokens": estimated_input, "reserved_output_tokens": reserved_output,
                "safety_tokens": opts["context_safety_tokens"], "context_window": context_window,
                "context_window_source": context_source, "request_sent": False,
                "context_window_verified": bool(context_source and "ollama_api_show" in context_source),
                "query_id": context.get("query_id")}
            return "error"
        output_options = ({"max_output_tokens": opts["max_output_tokens"]}
                          if opts["max_output_tokens"] is not None else {})
        answer = chat_once(messages, str(model), str(base_url), tools or None, timeout,
                           **output_options)
        if not answer.get("ok"):
            yield {"type": "error", "code": answer.get("code", "provider_error"),
                "error": str(answer.get("message") or answer.get("error") or "Falha do provider"),
                "http_status": answer.get("http_status"),
                "retry_after_seconds": answer.get("retry_after_seconds"),
                "model": model, "provider": provider_id, "request_sent": True,
                "query_id": context.get("query_id")}
            return "error"
        calls = answer.get("tool_calls")
        calls = [] if calls is None else calls
        content = answer.get("content")
        if (not _valid_tool_calls(calls) or
                (content is not None and not isinstance(content, str))):
            yield {"type": "error", "code": "invalid_provider_response",
                   "error": "Mensagem ou tool_calls inválidos do provedor"}
            return "error"
        usage = answer.get("usage")
        exact_usage = (isinstance(usage, dict)
            and type(usage.get("prompt_tokens")) is int and usage["prompt_tokens"] >= 0
            and type(usage.get("completion_tokens")) is int and usage["completion_tokens"] >= 0)
        if exact_usage:
            input_tokens = usage["prompt_tokens"]
            output_tokens = usage["completion_tokens"]
            count_source = "provider"
        else:
            input_tokens = estimated_input
            assistant_output = {"content": answer.get("content", ""),
                                "tool_calls": answer.get("tool_calls", [])}
            output_tokens = _estimate_tokens(json.dumps(assistant_output, ensure_ascii=False, default=str))
            count_source = "estimated_utf8_bytes_div_3"
        yield {"type": "usage", "provider": provider_id,
            "model": answer.get("actual_model") or model, "request_index": turn + 1,
            "query_id": context.get("query_id"),
            "input_tokens": input_tokens, "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "token_count_source": count_source, "token_counts_exact": exact_usage,
            "context_window": context_window, "context_window_source": context_source,
            "context_window_verified": bool(context_source and "ollama_api_show" in context_source),
            "estimated_input_tokens_for_preflight": estimated_input,
            "context_safety_tokens": opts["context_safety_tokens"]}
        if answer.get("content"):
            yield {"type": "text", "text": answer["content"]}
        if not calls:
            return "stop"
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
                             "content": json.dumps(output, ensure_ascii=False, default=str)})
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
            "detail": f"Endpoint /models acessível via {prov['id']} ({prov.get('model')}); contexto é declaração do catálogo e inferência não foi testada. SPEC-935-R649/R918.",
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
        "       [--context-window N] [--max-output-tokens N]\n"
        "O preflight usa estimativa de caracteres, não tokenizer; não trunca nem troca provider automaticamente.\n"
        "Override: OPENCODE_SDK_BASE_URL (+ OPENCODE_SDK_MODEL); custo do endpoint não avaliado."
    )


def _format_status() -> str:
    prov = detect_provider()
    return json.dumps(
        {"especificacao": SPEC_ID, "custo": "padrão local; override não avaliado",
         "provedor": prov, "licenca": "livre (Core)",
         "transporte": "HTTP OpenAI-compativel (stdlib)",
         "context_window": (prov or {}).get("context_window"),
         "context_window_scope": "declared_catalog_not_runtime_probe"},
        ensure_ascii=False, indent=2,
    )


def main(argv: Optional[List[str]] = None) -> int:
    import sys as _sys
    argv = list(_sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"--help", "-h", "help"}:
        print(
            "Uso: python3 -m integrations.opencode_agent_sdk <status|doctor|install|query|tools> [args...]\n"
            "  query --prompt '...' [--model M] [--base-url U] [--max-turns N] [--system S] "
            "[--context-window N] [--max-output-tokens N]"
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
        parser.add_argument("--context-window", type=int)
        parser.add_argument("--max-output-tokens", type=int)
        parser.add_argument("--context-safety-tokens", type=int, default=256)
        try:
            parsed = parser.parse_args(rest)
        except SystemExit as exc:
            return int(exc.code)
        try:
            opts = build_options(parsed.prompt, system_prompt=parsed.system,
                                 max_turns=parsed.max_turns,
                                 model=parsed.model, base_url=parsed.base_url,
                                 context_window=parsed.context_window,
                                 max_output_tokens=parsed.max_output_tokens,
                                 context_safety_tokens=parsed.context_safety_tokens)
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
