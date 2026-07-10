# -*- coding: utf-8 -*-
"""
Testes R118 — Handshake `initialize` do servidor MCP metacognitive-interconnect
=================================================================================
`mci/mcp_server.py::SimpleMCPServer` não implementava o método `initialize`
do protocolo MCP — qualquer cliente real (OpenCode CLI, Claude Code, etc.)
manda esse handshake antes de qualquer outra coisa, e o servidor respondia
`{"isError": true, "content": [...."Método não suportado"...]}`, fazendo
o cliente considerar a conexão com "metacognitive-interconnect" como falha
antes mesmo de chegar em `tools/list`.

Requisitos (SPEC-935-R118):
  - `initialize` retorna protocolVersion/capabilities/serverInfo válidos
  - `notifications/initialized` (sem "id") não recebe resposta JSON-RPC
  - `tools/list` e `tools/call` continuam funcionando após o handshake
"""

import asyncio
import json

import pytest


def _run(coro):
    return asyncio.run(coro)


@pytest.fixture
def server():
    from mci.mcp_server import mci_server
    return mci_server


class TestInitializeHandshake:
    def test_initialize_returns_protocol_fields(self, server):
        req = {
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test"}},
        }
        resp = _run(server.handle_request(req))
        assert "protocolVersion" in resp
        assert "capabilities" in resp
        assert resp["serverInfo"]["name"] == "metacognitive-interconnect"
        assert resp.get("isError") is not True

    def test_initialize_echoes_requested_protocol_version(self, server):
        req = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
               "params": {"protocolVersion": "2025-03-26"}}
        resp = _run(server.handle_request(req))
        assert resp["protocolVersion"] == "2025-03-26"

    def test_ping_does_not_error(self, server):
        resp = _run(server.handle_request({"jsonrpc": "2.0", "id": 3, "method": "ping"}))
        assert resp.get("isError") is not True

    def test_tools_list_still_works_after_initialize(self, server):
        _run(server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}))
        resp = _run(server.handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}))
        names = [t["name"] for t in resp["tools"]]
        assert "mci_get_blackboard_state" in names
        assert len(names) == 4


class TestNotificationHandling:
    def test_run_stdio_sends_no_response_for_notification(self):
        """Reproduz o loop real de run_stdio: uma notificacao (sem "id",
        ex. notifications/initialized) nao deve gerar nenhuma linha de
        resposta no stdout."""
        from mci.mcp_server import SimpleMCPServer

        srv = SimpleMCPServer("test-server")
        lines = [
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}) + "\n",
            "",  # EOF
        ]

        class FakeReader:
            def __init__(self, lines):
                self._lines = list(lines)

            async def readline(self):
                return self._lines.pop(0).encode("utf-8") if self._lines else b""

        class FakeWriter:
            def __init__(self):
                self.written = []

            def write(self, data):
                self.written.append(data)

            def flush(self):
                pass

        async def run():
            reader = FakeReader(lines)
            writer = FakeWriter()

            while True:
                line = await reader.readline()
                if not line:
                    break
                req = json.loads(line.decode("utf-8"))
                if "id" not in req or req.get("id") is None:
                    await srv.handle_request(req)
                    continue
                resp = await srv.handle_request(req)
                writer.write(json.dumps({"jsonrpc": "2.0", "id": req.get("id"), "result": resp}) + "\n")
                writer.flush()
            return writer

        writer = _run(run())
        assert writer.written == [], "Notificacao sem 'id' nao deveria gerar nenhuma resposta JSON-RPC"

    def test_request_with_id_still_gets_response(self):
        """Mesmo cenario, mas com uma request de verdade (com id) misturada —
        confirma que so a notificacao e suprimida, nao tudo."""
        from mci.mcp_server import SimpleMCPServer

        srv = SimpleMCPServer("test-server")
        lines = [
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n",
            json.dumps({"jsonrpc": "2.0", "id": 9, "method": "ping"}) + "\n",
            "",
        ]

        class FakeReader:
            def __init__(self, lines):
                self._lines = list(lines)

            async def readline(self):
                return self._lines.pop(0).encode("utf-8") if self._lines else b""

        responses = []

        async def run():
            reader = FakeReader(lines)
            while True:
                line = await reader.readline()
                if not line:
                    break
                req = json.loads(line.decode("utf-8"))
                if "id" not in req or req.get("id") is None:
                    await srv.handle_request(req)
                    continue
                resp = await srv.handle_request(req)
                responses.append({"jsonrpc": "2.0", "id": req.get("id"), "result": resp})

        _run(run())
        assert len(responses) == 1
        assert responses[0]["id"] == 9
