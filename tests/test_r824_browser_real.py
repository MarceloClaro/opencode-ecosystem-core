"""R824: configuração, fronteiras e execução real do provider de navegador."""
import json
import asyncio
from pathlib import Path

import pytest


def bridge(tmp_path):
    from integrations.browser_bridge import BrowserBridge
    return BrowserBridge(tmp_path)


@pytest.mark.parametrize("config", [
    None, [], {"operation": "unknown"}, {"operation": "run"},
    {"operation": []},
    {"operation": "run", "url": "file:///etc/passwd"},
    {"operation": "run", "url": "https://user:secret@example.org"},
    {"operation": "run", "url": "https://example.org", "timeout_seconds": True},
    {"operation": "run", "url": "https://example.org", "timeout_seconds": float("inf")},
    {"operation": "run", "url": "https://example.org", "javascript": "process.exit()"},
    {"operation": "run", "url": "https://example.org", "steps": [{"action": "evaluate", "code": "anything"}]},
    {"operation": "run", "url": "https://example.org", "steps": [{"action": []}]},
    {"operation": "run", "url": "https://example.org", "steps": [{"action": "fill", "role": "button", "name": "X", "value": "Y"}]},
    {"operation": "run", "url": "https://example.org", "allowed_origins": ["https://other.example"]},
])
def test_invalid_request_is_rejected_before_start(tmp_path, monkeypatch, config):
    instance = bridge(tmp_path)
    monkeypatch.setattr(instance, "status", lambda: pytest.fail("provider discovered before validating request"))
    with pytest.raises(ValueError):
        instance.action(config)


def test_status_never_starts_browser(tmp_path, monkeypatch):
    instance = bridge(tmp_path)
    monkeypatch.setattr(instance, "_exchange", lambda *_: pytest.fail("status started browser"))
    result = instance.action({"operation": "status"})
    assert result["verification"] == "installation_only"
    assert result["browser_executed"] is False


def test_action_serialization_does_not_interpolate_code(tmp_path):
    instance = bridge(tmp_path)
    payload = '"; process.exit(); // $(`id`)'
    step = {"action": "fill", "role": "textbox", "name": payload, "value": payload}
    code = instance._step_code(step)
    assert json.dumps(payload, ensure_ascii=False) in code
    assert "eval(" not in code and "exec(" not in code


def test_default_origin_is_canonical_and_explicit(tmp_path):
    config = bridge(tmp_path)._validate({"operation": "run", "url": "https://EXAMPLE.org:443/a"})
    assert config["allowed_origins"] == ["https://example.org"]


@pytest.mark.parametrize("field", ["url", "name", "value"])
def test_invalid_unicode_is_rejected_before_provider_discovery(tmp_path, monkeypatch, field):
    instance = bridge(tmp_path)
    config = {"operation": "run", "url": "https://example.org/page",
              "steps": [{"action": "fill", "role": "textbox", "name": "Mensagem", "value": "texto"}]}
    if field == "url":
        config["url"] += chr(0xD800)
    else:
        config["steps"][0][field] = chr(0xD800)
    monkeypatch.setattr(instance, "status", lambda: pytest.fail("provider discovered before UTF-8 validation"))
    with pytest.raises(ValueError, match="UTF-8"):
        instance.action(config)


def test_unavailable_provider_does_not_claim_execution(tmp_path, monkeypatch):
    instance = bridge(tmp_path)
    monkeypatch.setenv("CORE_BROWSER_HOME", str(tmp_path / "absent"))
    result = instance.action({"operation": "run", "url": "http://localhost:8000"})
    assert result["status"] == "unavailable" and not result["success"]
    assert result["browser_executed"] is False


def test_evidence_hash_mismatch_fails_closed(tmp_path):
    from integrations.browser_bridge import compact_browser_report
    result = compact_browser_report({"status": "completed", "success": True,
        "response": {"steps": []}, "response_sha256": "0" * 64}, tmp_path)
    assert result["status"] == "failed" and result["success"] is False


def test_evidence_is_complete_and_compact(tmp_path):
    from integrations.browser_bridge import compact_browser_report
    response = {"text": "x" * 25000}
    result = compact_browser_report({"status": "completed", "success": True,
                                    "response": response}, tmp_path)
    artifact = result["evidence_artifact"]
    assert json.loads(Path(artifact["path"]).read_text()) == response
    assert "response" not in result
    assert artifact["complete"] is True


@pytest.mark.parametrize("mode", ["http", "connect"])
def test_proxy_rejects_destination_before_contact(mode):
    from integrations.browser_proxy import BrowserOriginProxy
    from integrations.browser_bridge import _origin
    async def prove():
        contacts = []
        async def target(reader, writer):
            contacts.append(True)
            writer.close()
            await writer.wait_closed()
        server = await asyncio.start_server(target, "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        try:
            async with BrowserOriginProxy(["http://127.0.0.1:1"], _origin) as proxy:
                proxy_port = int(proxy.url.rsplit(":", 1)[1])
                reader, writer = await asyncio.open_connection("127.0.0.1", proxy_port)
                first = f"CONNECT 127.0.0.1:{port} HTTP/1.1" if mode == "connect" else f"GET http://127.0.0.1:{port}/trap HTTP/1.1"
                writer.write((first + "\r\nHost: localhost\r\n\r\n").encode())
                await writer.drain()
                assert b"403 Forbidden" in await asyncio.wait_for(reader.read(), 2)
                writer.close()
                await writer.wait_closed()
                assert not contacts
                assert proxy.decisions[0]["allowed"] is False
            assert not proxy.tasks
        finally:
            server.close()
            await server.wait_closed()
    asyncio.run(prove())


def test_proxy_forwards_authorized_http_and_preserves_resource():
    from integrations.browser_proxy import BrowserOriginProxy
    from integrations.browser_bridge import _origin
    async def prove():
        requests = []
        async def target(reader, writer):
            requests.append(await reader.readuntil(b"\r\n\r\n"))
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\nOK")
            await writer.drain()
            writer.close()
            await writer.wait_closed()
        server = await asyncio.start_server(target, "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        try:
            async with BrowserOriginProxy([f"http://127.0.0.1:{port}"], _origin) as proxy:
                reader, writer = await asyncio.open_connection("127.0.0.1", int(proxy.url.rsplit(":", 1)[1]))
                writer.write(f"GET http://127.0.0.1:{port}/a?q=1 HTTP/1.1\r\nHost: malicious.invalid\r\n\r\n".encode())
                await writer.drain()
                assert (await asyncio.wait_for(reader.read(), 2)).endswith(b"OK")
                writer.close()
                await writer.wait_closed()
            assert requests[0].startswith(b"GET /a?q=1 HTTP/1.1\r\n")
            assert f"Host: 127.0.0.1:{port}".encode() in requests[0]
            assert b"malicious.invalid" not in requests[0]
        finally:
            server.close()
            await server.wait_closed()
    asyncio.run(prove())


def test_proxy_connect_tunnel_and_shutdown_close_active_peers():
    from integrations.browser_proxy import BrowserOriginProxy
    from integrations.browser_bridge import _origin
    async def prove():
        stopped = asyncio.Event()
        async def echo(reader, writer):
            try:
                while data := await reader.read(4096):
                    writer.write(data)
                    await writer.drain()
            finally:
                writer.close()
                await writer.wait_closed()
                stopped.set()
        server = await asyncio.start_server(echo, "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        try:
            async with BrowserOriginProxy([f"https://127.0.0.1:{port}"], _origin) as proxy:
                reader, writer = await asyncio.open_connection("127.0.0.1", int(proxy.url.rsplit(":", 1)[1]))
                writer.write(f"CONNECT 127.0.0.1:{port} HTTP/1.1\r\n\r\n".encode())
                await writer.drain()
                assert b"200 Connection Established" in await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), 2)
                writer.write(b"PING")
                await writer.drain()
                assert await asyncio.wait_for(reader.readexactly(4), 2) == b"PING"
            assert await asyncio.wait_for(reader.read(), 2) == b""
            await asyncio.wait_for(stopped.wait(), 2)
            assert not proxy.tasks
            writer.close()
            await writer.wait_closed()
        finally:
            server.close()
            await server.wait_closed()
    asyncio.run(prove())


@pytest.mark.parametrize("cancel", [False, True])
def test_mcp_anyio_worker_can_start_private_loop_without_losing_cancel(tmp_path, monkeypatch, cancel):
    import anyio
    from threading import Event
    from integrations.execution_control import cancellation_scope, is_cancelled
    instance = bridge(tmp_path)
    monkeypatch.setattr(instance, "status", lambda: {"available": True, "provenance": {}})
    event = Event()
    async def exchange(request, inventory, captured, log):
        assert not is_cancelled()
        if cancel:
            event.set()
            assert is_cancelled()
    monkeypatch.setattr(instance, "_exchange", exchange)
    async def prove():
        with cancellation_scope(event):
            return await asyncio.to_thread(instance.action, {"operation": "run", "url": "https://example.org"})
    report = anyio.run(prove)
    assert report["status"] == ("cancelled" if cancel else "completed"), report.get("error")
    assert report["success"] is not cancel


@pytest.mark.parametrize("available", [False, True])
def test_doctor_reports_browser_installation_without_launch(monkeypatch, available):
    from marceloclaro import doctor
    from integrations.browser_bridge import BrowserBridge
    calls = []
    def status(self):
        calls.append(True)
        return {"available": available, "provenance": {"version": "0.0.83"}, "error": "ausente"}
    monkeypatch.setattr(BrowserBridge, "status", status)
    monkeypatch.setattr(BrowserBridge, "action", lambda *_: pytest.fail("doctor launched browser"))
    result = doctor._check_browser()
    assert calls == [True]
    assert result.status == ("pass" if available else "warn")
    assert "execução" in result.detail or "indisponível" in result.detail
