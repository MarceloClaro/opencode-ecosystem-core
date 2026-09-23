"""Testes do web-deploy-mcp (SPEC-974, R581).

Cobertura hermética: servidor HTTP local, diretórios temporários e
GH_API_BASE sobrescrito — nenhuma rede externa, nenhum token real.
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

_MODULE_PATH = (
    Path(__file__).resolve().parents[1] / ".opencode" / "mcp" / "web_deploy_server.py"
)
_spec = importlib.util.spec_from_file_location("web_deploy_server", _MODULE_PATH)
assert _spec and _spec.loader, f"spec inválida para {_MODULE_PATH}"
web_deploy_server = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(web_deploy_server)

DEFAULT_LIMIT_MB = web_deploy_server.DEFAULT_LIMIT_MB
_assert_gone = web_deploy_server._assert_gone
_pages_status = web_deploy_server._pages_status
_probe_url = web_deploy_server._probe_url
_site_weight = web_deploy_server._site_weight
_validate_feed = web_deploy_server._validate_feed
_call_tool = web_deploy_server.call_tool


def _txt(out) -> str:
    """Extrai texto de CallToolResult (isError) ou list[TextContent] (ok)."""
    if isinstance(out, list):
        return out[0].text
    return out.content[0].text


# ── servidor HTTP local (provas de 200/206/404) ──────────────────────────────


class _Handler(BaseHTTPRequestHandler):
    _payload = b"<html>MOLAMBUDOS-NOVA-FLAG</html>"

    def do_GET(self):  # noqa: N802
        if self.path.startswith("/gone"):
            self.send_response(404)
            self.end_headers()
            return
        if self.path.startswith("/audio"):
            range_header = self.headers.get("Range")
            if range_header:
                self.send_response(206)
                self.send_header("Content-Range", "bytes 0-9/27")
                self.send_header("Content-Length", "10")
                self.end_headers()
                self.wfile.write(self._payload[:10])
                return
            self.send_response(200)
            self.send_header("Content-Type", "audio/mp4")
            self.send_header("Content-Length", str(len(self._payload)))
            self.end_headers()
            self.wfile.write(self._payload)
            return
        self.send_response(200)
        self.send_header("Content-Length", str(len(self._payload)))
        self.end_headers()
        self.wfile.write(self._payload)

    def log_message(self, *args):  # noqa: D102
        pass


@pytest.fixture(scope="module")
def local_http():
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    thread.join(timeout=3)


# ── probe_url: a lição central R571 (GET+Range, nunca HEAD) ──────────────────


def test_probe_url_200_e_marker(local_http):
    out = asyncio.run(_probe_url({"url": f"{local_http}/index.html", "marker": "NOVA-FLAG"}))
    assert "status=200" in _txt(out)
    assert "encontrado=True" in _txt(out)


def test_probe_url_range_206(local_http):
    out = asyncio.run(_probe_url({"url": f"{local_http}/audio/ep.m4a", "range_first": True}))
    assert "status=206" in _txt(out)
    assert "range=True" in _txt(out)


def test_probe_url_404(local_http):
    out = asyncio.run(_probe_url({"url": f"{local_http}/gone"}))
    assert "status=404" in _txt(out)


def test_probe_url_invalida_fail_closed():
    out = asyncio.run(_probe_url({"url": "not-a-url"}))
    assert _txt(out).startswith("ERRO:")


# ── assert_gone: remoções viraram 404 de verdade ─────────────────────────────


def test_assert_gone_todos_404(local_http):
    out = asyncio.run(_assert_gone({"urls": [f"{local_http}/gone", f"{local_http}/gone2"]}))
    assert "TODOS 404" in _txt(out)


def test_assert_gone_falha_se_200(local_http):
    out = asyncio.run(_assert_gone({"urls": [f"{local_http}/index.html"]}))
    assert "FALHA" in _txt(out)
    assert "200" in _txt(out)


# ── site_weight: guards 1GB / 25MiB ──────────────────────────────────────────


def test_site_weight_granted_e_exclui_git(tmp_path: Path):
    (tmp_path / "a.txt").write_bytes(b"x" * 1000)
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.bin").write_bytes(b"y" * 2000)
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "big").write_bytes(b"z" * 500000)
    out = asyncio.run(_site_weight({"path": str(tmp_path)}))
    assert "status=GRANTED" in _txt(out)
    # .git (500 KB) excluído => total ~3 KB
    assert "total=0 MiB" in _txt(out) or "total=1 MiB" in _txt(out)


def test_site_weight_denied_por_arquivo(tmp_path: Path):
    (tmp_path / "huge.bin").write_bytes(b"x" * (26 * 1024 * 1024))
    out = asyncio.run(_site_weight({"path": str(tmp_path), "max_file_mb": 25}))
    assert "status=DENIED" in _txt(out)
    assert "oversize" in _txt(out)


# ── validate_feed: enclosure length + guid ───────────────────────────────────


def test_validate_feed_granted(tmp_path: Path):
    feed = tmp_path / "feed.xml"
    (tmp_path / "ep01.m4a").write_bytes(b"audio")
    feed.write_text(
        '<?xml version="1.0"?><rss><channel>'
        "<item><title>Ep1</title>"
        '<enclosure url="https://x/ep01.m4a" length="5" type="audio/mp4"/>'
        "<guid>sha256:abc</guid><link>https://x</link></item>"
        "</channel></rss>",
        encoding="utf-8",
    )
    out = asyncio.run(_validate_feed({"feed_path": str(feed), "root_dir": str(tmp_path)}))
    assert "status=GRANTED" in _txt(out)


def test_validate_feed_denied_sem_length(tmp_path: Path):
    feed = tmp_path / "feed_bad.xml"
    feed.write_text(
        '<rss><channel><item><title>Ep1</title>'
        '<enclosure url="https://x/ep01.m4a" type="audio/mp4"/>'
        "<guid>g1</guid></item></channel></rss>",
        encoding="utf-8",
    )
    out = asyncio.run(_validate_feed({"feed_path": str(feed)}))
    assert "status=DENIED" in _txt(out)
    assert "sem length" in _txt(out)


# ── pages_status: mulher do token usando GH_API_BASE local ──────────────────


@pytest.fixture()
def fake_pages_server():
    class PHandler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            body = json.dumps(
                {"status": "built", "duration": 83, "error": None}
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):  # noqa: D102
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), PHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    thread.join(timeout=3)


def test_pages_status_ok(monkeypatch, fake_pages_server):
    monkeypatch.setenv("GH_API_BASE", fake_pages_server)
    monkeypatch.setenv("GITHUB_TOKEN", "x" * 40)
    out = asyncio.run(_pages_status({"owner": "usuario", "repo": "site"}))
    assert "status=built" in _txt(out)
    assert "duration=83" in _txt(out)


def test_pages_status_sem_token_fail_closed(monkeypatch, fake_pages_server):
    monkeypatch.setenv("GH_API_BASE", fake_pages_server)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setenv("HOME", "/tmp/opencode/no-credentials")
    out = asyncio.run(_pages_status({"owner": "u", "repo": "r"}))
    assert _txt(out).startswith("ERRO:")


if __name__ == "__main__":
    pytest.main([__file__, "-q"])

# ── regressão do shape MCP (R582): lista/CallToolResult, nunca TextContent solto
# ── (bug descoberto após restart: retorno solto virava tuplas no transporte)


def test_ok_retorna_lista_de_textcontent():
    out = web_deploy_server._ok("mensagem")
    assert isinstance(out, list)
    assert out[0].text == "mensagem"


def test_mcp_error_retorna_calltoolresult_com_iserror():
    out = web_deploy_server._mcp_error("falha x")
    assert getattr(out, "isError", False) is True
    assert out.content[0].text.startswith("ERRO: falha x")


def test_call_tool_ferramenta_ok_retorna_lista(tmp_path: Path):
    (tmp_path / "f.txt").write_bytes(b"abc")
    out = asyncio.run(_call_tool("web_deploy_site_weight", {"path": str(tmp_path)}))
    assert isinstance(out, list)
