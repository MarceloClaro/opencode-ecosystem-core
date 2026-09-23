#!/usr/bin/env python3
"""Prova hermética do protocolo MCP do web-deploy-server (R582).

Sobe o servidor via stdio e faz o handshake completo:
initialize -> initialized -> tools/list -> tools/call (site_weight).

Objetivo: provar que o shape corrigido (list[TextContent] / CallToolResult)
é válido no TRANSPORTE real (JSON-RPC newline-delimited), não só no Python.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / ".opencode" / "mcp" / "web_deploy_server.py"

proc = subprocess.Popen(
    [sys.executable, str(SERVER)],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)


def send(payload: dict) -> dict:
    proc.stdin.write(json.dumps(payload) + "\n")
    proc.stdin.flush()
    line = proc.stdout.readline()
    while line and line.strip() == "":
        line = proc.stdout.readline()
    return json.loads(line)


try:
    # 1. initialize
    resp = send({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                   "clientInfo": {"name": "prova-hermetica", "version": "0.1"}},
    })
    assert "result" in resp, f"initialize falhou: {resp}"
    print("initialize OK:", resp["result"]["serverInfo"])

    # 2. initialized (notification, sem resposta)
    proc.stdin.write(json.dumps({
        "jsonrpc": "2.0", "method": "notifications/initialized", "params": {},
    }) + "\n")
    proc.stdin.flush()

    # 3. tools/list
    resp = send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    tools = [t["name"] for t in resp["result"]["tools"]]
    assert len(tools) == 5, tools
    print("tools/list OK:", tools)

    # 4. tools/call — site_weight em dir temporário (shape corrigido!)
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "a.txt").write_text("abc")
        resp = send({
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": "web_deploy_site_weight", "arguments": {"path": tmp}},
        })
    content = resp["result"]["content"]
    assert isinstance(content, list) and content, "content não é lista"
    assert content[0]["type"] == "text", content
    assert "GRANTED" in content[0]["text"], content
    print("tools/call OK — content[0] =", content[0]["text"].splitlines()[0])

    print("\nPROTOCOLO MCP OK (shape válido no transporte)")
finally:
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()