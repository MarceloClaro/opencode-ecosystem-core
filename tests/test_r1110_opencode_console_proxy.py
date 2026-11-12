"""R1110 — testes herméticos do proxy local do `opencode_console`."""

from __future__ import annotations

import json
import logging
import sqlite3
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from scripts.opencode_console_proxy import (
    ProxyHandler,
    TokenError,
    check,
    read_member_token,
)


def _make_db(tmp_path, rows):
    db = tmp_path / "opencode.db"
    con = sqlite3.connect(db)
    con.execute(
        "create table credential ("
        "id text, integration_id text, label text, value text, "
        "connector_id text, method_id text, active integer, "
        "time_created integer, time_updated integer)"
    )
    for idx, (integration, value, active, updated) in enumerate(rows):
        con.execute(
            "insert into credential values (?,?,?,?,?,?,?,?,?)",
            (f"cred_{idx}", integration, "test", json.dumps(value), None, None,
             active, updated, updated),
        )
    con.commit()
    con.close()
    return db


def _credential(token: str, expires_ms: int) -> dict:
    return {"type": "oauth", "access": token, "expires": expires_ms}


def test_read_member_token_returns_latest_active(tmp_path):
    now_ms = int(time.time() * 1000)
    db = _make_db(tmp_path, [
        ("opencode", _credential("old-token", now_ms + 3_600_000), 1, 1),
        ("opencode", _credential("new-token", now_ms + 3_600_000), 1, 2),
        ("opencode", _credential("inactive-token", now_ms + 3_600_000), 0, 3),
        ("other", _credential("other-token", now_ms + 3_600_000), 1, 4),
    ])

    assert read_member_token(db) == "new-token"


def test_read_member_token_rejects_expired(tmp_path):
    now_ms = int(time.time() * 1000)
    db = _make_db(tmp_path, [
        ("opencode", _credential("expired", now_ms - 1), 1, 1),
    ])

    with pytest.raises(TokenError, match="expired"):
        read_member_token(db)


def test_read_member_token_rejects_missing(tmp_path):
    db = _make_db(tmp_path, [])

    with pytest.raises(TokenError, match="missing"):
        read_member_token(db)


def test_read_member_token_rejects_empty_access(tmp_path):
    now_ms = int(time.time() * 1000)
    db = _make_db(tmp_path, [
        ("opencode", {"type": "oauth", "access": "", "expires": now_ms + 3_600_000}, 1, 1),
    ])

    with pytest.raises(TokenError, match="access token"):
        read_member_token(db)


def test_read_member_token_rejects_invalid_json(tmp_path):
    db = tmp_path / "opencode.db"
    con = sqlite3.connect(db)
    con.execute(
        "create table credential (id text, integration_id text, label text, "
        "value text, connector_id text, method_id text, active integer, "
        "time_created integer, time_updated integer)"
    )
    con.execute(
        "insert into credential values ('1','opencode','test','not-json',"
        "null,null,1,1,1)"
    )
    con.commit()
    con.close()

    with pytest.raises(TokenError, match="JSON"):
        read_member_token(db)


class _UpstreamHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    requests: list[dict] = []
    response_status = 200
    response_body = b'event: message\ndata: {"jsonrpc":"2.0","id":1,"result":{}}\n\n'
    response_headers = {"Content-Type": "text/event-stream"}

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        type(self).requests.append({
            "method": "POST",
            "path": self.path,
            "headers": dict(self.headers),
            "body": body,
        })
        self.send_response(type(self).response_status)
        for name, value in type(self).response_headers.items():
            self.send_header(name, value)
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(type(self).response_body)
        self.wfile.flush()

    def log_message(self, *args):
        return


@pytest.fixture
def upstream():
    _UpstreamHandler.requests = []
    _UpstreamHandler.response_status = 200
    _UpstreamHandler.response_body = (
        b'event: message\ndata: {"jsonrpc":"2.0","id":1,"result":{}}\n\n'
    )
    _UpstreamHandler.response_headers = {"Content-Type": "text/event-stream"}
    server = ThreadingHTTPServer(("127.0.0.1", 0), _UpstreamHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()
    server.server_close()


def _start_proxy(upstream, db):
    class Handler(ProxyHandler):
        upstream_url = f"http://127.0.0.1:{upstream.server_port}/mcp"
        db_path = db

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def _post(proxy, body=b'{"jsonrpc":"2.0","id":1,"method":"initialize"}'):
    request = urllib.request.Request(
        f"http://127.0.0.1:{proxy.server_port}/mcp",
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", "Accept": "text/event-stream"},
    )
    return urllib.request.urlopen(request, timeout=10)


def test_proxy_injects_member_token_and_streams_sse(tmp_path, upstream):
    now_ms = int(time.time() * 1000)
    db = _make_db(tmp_path, [
        ("opencode", _credential("test-token", now_ms + 3_600_000), 1, 1),
    ])
    proxy = _start_proxy(upstream, db)
    try:
        with _post(proxy) as response:
            body = response.read()
        assert response.status == 200
        assert body == _UpstreamHandler.response_body
        assert _UpstreamHandler.requests[-1]["headers"]["Authorization"] == "Bearer test-token"
        assert b"test-token" not in body
    finally:
        proxy.shutdown()
        proxy.server_close()


def test_proxy_rejects_missing_token_without_calling_upstream(tmp_path, upstream):
    db = _make_db(tmp_path, [])
    proxy = _start_proxy(upstream, db)
    try:
        with pytest.raises(urllib.error.HTTPError) as excinfo:
            _post(proxy)
        assert excinfo.value.code == 401
        assert b"connect" in excinfo.value.read().lower()
        assert _UpstreamHandler.requests == []
    finally:
        proxy.shutdown()
        proxy.server_close()


def test_proxy_rejects_expired_token(tmp_path, upstream):
    now_ms = int(time.time() * 1000)
    db = _make_db(tmp_path, [
        ("opencode", _credential("expired-token", now_ms - 1), 1, 1),
    ])
    proxy = _start_proxy(upstream, db)
    try:
        with pytest.raises(urllib.error.HTTPError) as excinfo:
            _post(proxy)
        assert excinfo.value.code == 401
        assert _UpstreamHandler.requests == []
    finally:
        proxy.shutdown()
        proxy.server_close()


def test_proxy_forwards_upstream_error(tmp_path, upstream):
    _UpstreamHandler.response_status = 403
    _UpstreamHandler.response_body = b'{"error":"forbidden"}'
    _UpstreamHandler.response_headers = {"Content-Type": "application/json"}
    now_ms = int(time.time() * 1000)
    db = _make_db(tmp_path, [
        ("opencode", _credential("test-token", now_ms + 3_600_000), 1, 1),
    ])
    proxy = _start_proxy(upstream, db)
    try:
        with pytest.raises(urllib.error.HTTPError) as excinfo:
            _post(proxy)
        assert excinfo.value.code == 403
        assert excinfo.value.read() == b'{"error":"forbidden"}'
    finally:
        proxy.shutdown()
        proxy.server_close()


def test_proxy_does_not_log_token(tmp_path, upstream, caplog):
    now_ms = int(time.time() * 1000)
    db = _make_db(tmp_path, [
        ("opencode", _credential("secret-token", now_ms + 3_600_000), 1, 1),
    ])
    proxy = _start_proxy(upstream, db)
    caplog.set_level(logging.INFO)
    try:
        with _post(proxy) as response:
            response.read()
        assert "secret-token" not in caplog.text
    finally:
        proxy.shutdown()
        proxy.server_close()


def test_check_reports_success_without_exposing_token(tmp_path, upstream, capsys):
    now_ms = int(time.time() * 1000)
    db = _make_db(tmp_path, [
        ("opencode", _credential("check-token", now_ms + 3_600_000), 1, 1),
    ])
    url = f"http://127.0.0.1:{upstream.server_port}/mcp"

    assert check(url, db) == 0
    captured = capsys.readouterr()
    assert "check-token" not in captured.out
    assert "check-token" not in captured.err


def test_check_reports_upstream_error(tmp_path, upstream, capsys):
    _UpstreamHandler.response_status = 403
    _UpstreamHandler.response_body = b'{"error":"forbidden"}'
    _UpstreamHandler.response_headers = {"Content-Type": "application/json"}
    now_ms = int(time.time() * 1000)
    db = _make_db(tmp_path, [
        ("opencode", _credential("check-token", now_ms + 3_600_000), 1, 1),
    ])
    url = f"http://127.0.0.1:{upstream.server_port}/mcp"

    assert check(url, db) == 1
    captured = capsys.readouterr()
    assert "403" in captured.out
    assert "check-token" not in captured.out
    assert "check-token" not in captured.err
