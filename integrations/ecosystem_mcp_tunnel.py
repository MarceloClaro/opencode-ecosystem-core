"""R1222: bridge stdio que responde `server/discover` sem alterar o MCP real.

O cliente OpenAI pode enviar `server/discover` (spec 2026-07-28) a um servidor
que implementa apenas a versão `2025-11-25`. Este bridge responde a esse único
método e encaminha todo o restante para `integrations.ecosystem_mcp`.

Não anunciamos `2026-07-28`: a resposta é apenas compatibilidade de
descoberta, não uma implementação das semânticas do protocolo moderno.
"""
from __future__ import annotations

import asyncio
import json
import subprocess
import sys
import threading
from collections.abc import Awaitable, Callable
from typing import Any

CHILD_MODULE = "integrations.ecosystem_mcp"
DISCOVER_METHOD = "server/discover"
SUPPORTED_VERSION = "2025-11-25"
SERVER_NAME = "ecosystem-network"
SERVER_VERSION = "1.28.1"
CAPABILITIES = {
    "prompts": {},
    "resources": {},
    "tools": {"listChanged": False},
}
Send = Callable[[str], Awaitable[None]]


def make_discover_result(request_id: Any) -> dict[str, Any]:
    """Resposta determinística e conservadora para `server/discover`."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "resultType": "complete",
            "supportedVersions": [SUPPORTED_VERSION],
            "capabilities": dict(CAPABILITIES),
            "instructions": (
                "Servidor MCP 2025-11-25 do OpenCode Ecosystem Core; "
                "use tools/list e tools/call."
            ),
            "_meta": {
                "io.modelcontextprotocol.serverInfo": {
                    "name": SERVER_NAME,
                    "version": SERVER_VERSION,
                }
            },
            "ttlMs": 0,
            "cacheScope": "private",
        },
    }


def is_discover_request(payload: Any) -> bool:
    """Somente requests com id recebem resposta; notificações são ignoradas."""
    return (
        isinstance(payload, dict)
        and payload.get("method") == DISCOVER_METHOD
        and "id" in payload
    )


async def process_line(line: str, send: Send) -> str | None:
    """Processa uma linha; retorna a resposta gerada ou ``None`` se repassou."""
    try:
        payload = json.loads(line)
    except (TypeError, ValueError):
        await send(line)
        return None
    if not is_discover_request(payload):
        await send(line)
        return None
    response = json.dumps(make_discover_result(payload["id"]), ensure_ascii=False)
    await send(response + "\n")
    return response


def _forward_stream(source: Any, destination: Any) -> None:
    try:
        for line in source:
            destination.write(line)
            destination.flush()
    except (BrokenPipeError, ValueError):
        return


def main() -> int:
    child = subprocess.Popen(
        [sys.executable, "-B", "-m", CHILD_MODULE],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    threads = (
        threading.Thread(
            target=_forward_stream,
            args=(child.stdout, sys.stdout),
            name="r1222-stdout",
            daemon=True,
        ),
        threading.Thread(
            target=_forward_stream,
            args=(child.stderr, sys.stderr),
            name="r1222-stderr",
            daemon=True,
        ),
    )
    for thread in threads:
        thread.start()

    async def send(line: str) -> None:
        assert child.stdin is not None
        child.stdin.write(line)
        child.stdin.flush()

    try:
        for line in sys.stdin:
            asyncio.run(process_line(line, send))
    except (BrokenPipeError, KeyboardInterrupt):
        pass
    finally:
        if child.stdin is not None and not child.stdin.closed:
            try:
                child.stdin.close()
            except BrokenPipeError:
                pass
        code = child.wait()
        for thread in threads:
            thread.join(timeout=5)
    return code or 0


if __name__ == "__main__":
    raise SystemExit(main())
