"""Prova opcional real SDK → hooks → tool local → modelo, sem respostas falsas.

Executar explicitamente: .venv/bin/python scripts/probe_sdk_hooks_live.py
Ollama deve estar disponível com o modelo pedido. Só a soma em processo executa.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hooks.engine import HookMatcher
from integrations import opencode_agent_sdk as sdk


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:11434/v1")
    parser.add_argument("--model", default="qwen3:8b")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--deny-only", action="store_true")
    parser.add_argument("--output", default="docs/evidence/R659_SDK_HOOKS_LIVE.json")
    args = parser.parse_args()
    trace, executions = [], []
    phase = "allow"
    started = time.monotonic()
    started_at = datetime.now(timezone.utc).isoformat()
    code_hashes = {name: hashlib.sha256(Path(name).read_bytes()).hexdigest()
                  for name in ("integrations/opencode_agent_sdk.py", "hooks/engine.py",
                               "hooks/policy.py", "integrations/mcp_validation.py",
                               "scripts/probe_sdk_hooks_live.py")}

    @sdk.tool("somar_inteiros", "Soma dois inteiros e retorna o resultado exato.", {
        "type": "object", "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
        "required": ["a", "b"], "additionalProperties": False,
    })
    def somar(data):
        result = {"resultado": data["a"] + data["b"]}
        executions.append({"phase": phase, "args": data.copy(), "output": result.copy()})
        trace.append({"kind": "native_tool", "phase": phase, "args": data.copy(), "output": result.copy()})
        return result

    def observe(name, data, context):
        record = {"kind": "hook", "phase": phase, "event": context["event"], "tool": name,
                  "tool_call_id": context.get("tool_call_id"), "finish": context.get("finish")}
        if "output" in context:
            record["output"] = context["output"]
        trace.append(record)
        if phase == "deny" and context["event"] == "PreToolUse":
            return {"deny": True, "reason": "bloqueio explícito de prova R659"}

    original = sdk._http_json

    def traced_http(method, url, payload=None, timeout=5):
        call_started = time.monotonic()
        if payload is not None:
            payload = {**payload, "temperature": 0}
        request_snapshot = json.loads(json.dumps(payload))
        print(json.dumps({"phase": phase, "event": "http_started", "timeout": timeout}), flush=True)
        result = original(method, url, payload, timeout)
        print(json.dumps({"phase": phase, "event": "http_finished",
                          "elapsed_seconds": round(time.monotonic() - call_started, 3),
                          "response_received": result is not None}), flush=True)
        trace.append({"kind": "real_http", "phase": phase,
                      "elapsed_seconds": round(time.monotonic() - call_started, 3),
                      "method": method, "url": url,
                      "request": request_snapshot, "response": result})
        return result

    prompt = ('Use obrigatoriamente a ferramenta somar_inteiros com os argumentos JSON '
              '{"a":13,"b":29}. a e b devem ser números inteiros JSON sem aspas. '
              'Após obter o resultado, responda em português com o valor retornado.')
    options = sdk.build_options(
        prompt, model=args.model, base_url=args.base_url, max_turns=3,
        allowed_tools=["somar_inteiros"], timeout=args.timeout,
        system_prompt="Você é um assistente local. Para esta tarefa, chame a ferramenta disponibilizada antes de responder; não calcule sem consultar a ferramenta.",
        hooks={
            "SessionStart": [observe],
            "matchers": [HookMatcher("somar_*", [observe])],
            "PostToolUse": [HookMatcher("somar_*", [observe])],
            "SessionEnd": [observe],
        },
    )
    try:
        sdk._http_json = traced_http
        events = [] if args.deny_only else list(sdk.query(prompt, options))
        phase = "deny"
        denial_events = list(sdk.query(prompt, {**options, "max_turns": 1}))
    finally:
        sdk._http_json = original
        sdk._TOOLS.pop("somar_inteiros", None)
    lifecycle = [item["event"] for item in trace if item["kind"] == "hook" and item["phase"] == "allow"]
    allowed_success = None if args.deny_only else (executions == [{"phase": "allow", "args": {"a": 13, "b": 29}, "output": {"resultado": 42}}]
               and lifecycle == ["SessionStart", "PreToolUse", "PostToolUse", "SessionEnd"]
               and events[-1] == {"type": "result", "finish": "stop"}
               and any(event["type"] == "text" and "42" in event["text"] for event in events)
               and not any(event["type"] == "error" for event in events))
    denial_success = (any(event["type"] == "tool_denied" and "bloqueio explícito" in event["reason"]
                          for event in denial_events)
                      and not any(event["type"] == "tool_use" for event in denial_events)
                      and denial_events[-1] == {"type": "result", "finish": "max_turns"})
    success = allowed_success is not False and denial_success
    result = {"spec_id": "SPEC-935-R659", "ts": datetime.now(timezone.utc).isoformat(),
              "started_at": started_at, "elapsed_seconds": round(time.monotonic() - started, 3),
              "evidence_kind": "real_local_http_inference_and_native_tool", "success": success,
              "transport": "HTTP OpenAI-compatible", "tool_execution": "native_in_process_not_MCP",
              "allowed_success": allowed_success, "denial_success": denial_success,
              "scope": "deny_only" if args.deny_only else "allow_and_deny",
              "model": args.model, "base_url": args.base_url, "prompt": prompt,
              "executions": executions, "events": events, "denial_events": denial_events, "trace": trace,
              "code_sha256": code_hashes}
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"success": success, "output": str(path), "lifecycle": lifecycle,
                      "executions": executions, "events": events}, ensure_ascii=False))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
