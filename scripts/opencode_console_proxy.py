#!/usr/bin/env python3
"""Proxy local do MCP `opencode_console` (SPEC-935-R1110).

O servidor embutido `opencode_console` usa OAuth, mas o resource server do
Console rejeita o token OAuth com HTTP 403 neste workspace. O token de membro
da integração `opencode` é aceito. Este proxy lê esse token do banco local do
OpenCode a cada requisição, injeta o header `Authorization` e encaminha o
transporte Streamable HTTP para `https://opencode.ai/console/mcp`.

Escuta apenas em loopback. Não grava o token em disco, não o registra em log e
não tenta refresh próprio: após `/connect`, o novo token é lido do banco.
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

DEFAULT_UPSTREAM_URL = "https://opencode.ai/console/mcp"
DEFAULT_DB_PATH = Path.home() / ".local/share/opencode/opencode.db"
MEMBER_INTEGRATION = "opencode"
TOKEN_MARGIN_SECONDS = 60
MAX_BODY_BYTES = 10 * 1024 * 1024
UPSTREAM_TIMEOUT_SECONDS = 600

HOP_BY_HOP = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}
FORWARD_REQUEST_HEADERS = {
    "content-type",
    "accept",
    "mcp-session-id",
    "mcp-protocol-version",
    "last-event-id",
}
FORWARD_RESPONSE_HEADERS = {
    "content-type",
    "content-encoding",
    "cache-control",
    "mcp-session-id",
    "mcp-protocol-version",
    "location",
    "retry-after",
}
SECRET_RE = re.compile(r"(st_|oc_sk_|sk_)[A-Za-z0-9_\-]+")


class TokenError(RuntimeError):
    """Credencial de membro ausente, inválida ou expirada."""


def _parse_credential(value: str) -> dict:
    try:
        data = json.loads(value)
    except (TypeError, json.JSONDecodeError) as exc:
        raise TokenError("member credential is not valid JSON; run /connect") from exc
    if not isinstance(data, dict):
        raise TokenError("member credential has an unexpected shape; run /connect")
    return data


def _expires_ms(value) -> int | None:
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def read_member_token(db_path: Path | str = DEFAULT_DB_PATH, now: float | None = None) -> str:
    """Lê a credencial ativa mais recente da integração `opencode`."""
    db_path = Path(db_path)
    if not db_path.exists():
        raise TokenError("OpenCode database not found; run /connect in OpenCode")
    current = time.time() if now is None else now
    con = None
    try:
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=5)
        con.execute("pragma busy_timeout=5000")
        row = con.execute(
            "select value from credential where integration_id=? and active=1 "
            "order by time_updated desc limit 1",
            (MEMBER_INTEGRATION,),
        ).fetchone()
    except sqlite3.Error as exc:
        raise TokenError(f"cannot read OpenCode credentials: {exc}") from exc
    finally:
        if con is not None:
            con.close()
    if not row:
        raise TokenError("member credential missing; run /connect in OpenCode")

    data = _parse_credential(row[0])
    access = data.get("access")
    if not isinstance(access, str) or not access.strip():
        raise TokenError("member credential has no access token; run /connect")
    expires = _expires_ms(data.get("expires"))
    if expires is not None and expires / 1000.0 <= current + TOKEN_MARGIN_SECONDS:
        raise TokenError("member token expired or expiring; run /connect to renew")
    return access


def _sanitize(value: str) -> str:
    return SECRET_RE.sub("<redacted>", value)


def _server_name(payload: str) -> str | None:
    match = re.search(r'"name"\s*:\s*"([^"]+)"', payload)
    return match.group(1) if match else None


def _hostname(host_header: str) -> str:
    if host_header.startswith("["):
        end = host_header.find("]")
        return host_header[1:end].lower() if end > 0 else ""
    return host_header.split(":", 1)[0].strip().lower()


class ProxyHandler(BaseHTTPRequestHandler):
    """Encaminha requisições MCP para o Console com o token de membro."""

    protocol_version = "HTTP/1.1"
    server_version = "opencode-console-proxy/1.0"
    upstream_url = DEFAULT_UPSTREAM_URL
    db_path = DEFAULT_DB_PATH

    def log_message(self, fmt, *args):
        logging.info("%s - %s", self.address_string(), fmt % args)

    def _send_json(self, status: int, error: str, message: str) -> None:
        body = json.dumps({"error": error, "message": message}, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()

    def _loopback_only(self) -> bool:
        if self.client_address[0] not in {"127.0.0.1", "::1"}:
            self._send_json(403, "forbidden", "proxy accepts loopback clients only")
            return False
        if _hostname(self.headers.get("Host", "")) not in {"127.0.0.1", "localhost", "::1"}:
            self._send_json(403, "forbidden", "invalid Host header")
            return False
        return True

    def _read_body(self) -> bytes:
        raw = self.headers.get("Content-Length")
        if not raw:
            return b""
        try:
            length = int(raw)
        except ValueError as exc:
            raise ValueError("invalid Content-Length") from exc
        if length < 0 or length > MAX_BODY_BYTES:
            raise ValueError("request body too large")
        return self.rfile.read(length) if length else b""

    def _target_url(self) -> str:
        parts = urlsplit(self.path)
        return f"{self.upstream_url}?{parts.query}" if parts.query else self.upstream_url

    def _relay(self, status: int, headers, body) -> None:
        self.send_response(status)
        content_length = headers.get("Content-Length")
        for name, value in headers.items():
            lower = name.lower()
            if lower in HOP_BY_HOP or lower == "content-length":
                continue
            if lower in FORWARD_RESPONSE_HEADERS or lower.startswith("x-"):
                self.send_header(name, value)
        if content_length is not None:
            self.send_header("Content-Length", content_length)
        else:
            self.send_header("Connection", "close")
        self.end_headers()
        try:
            while True:
                chunk = body.read(65536)
                if not chunk:
                    break
                self.wfile.write(chunk)
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            return

    def _forward(self, method: str) -> None:
        if not self._loopback_only():
            return
        try:
            body = self._read_body() if method in {"POST", "PUT", "PATCH"} else b""
            token = read_member_token(self.db_path)
        except TokenError as exc:
            self._send_json(401, "unauthorized", str(exc))
            return
        except ValueError as exc:
            self._send_json(400, "bad_request", str(exc))
            return

        headers = {
            name: value
            for name, value in self.headers.items()
            if name.lower() in FORWARD_REQUEST_HEADERS
        }
        headers["Authorization"] = f"Bearer {token}"
        headers["Accept-Encoding"] = "identity"
        headers["User-Agent"] = "opencode-console-proxy/1.0"
        request = urllib.request.Request(
            self._target_url(), data=body or None, method=method, headers=headers
        )
        logging.info("proxy %s %s", method, urlsplit(self.path).path)
        try:
            with urllib.request.urlopen(request, timeout=UPSTREAM_TIMEOUT_SECONDS) as response:
                self._relay(response.status, response.headers, response)
        except urllib.error.HTTPError as exc:
            self._relay(exc.code, exc.headers, exc)
        except urllib.error.URLError as exc:
            self._send_json(502, "bad_gateway", f"upstream unavailable: {exc.reason}")
        except TimeoutError:
            self._send_json(504, "gateway_timeout", "upstream timed out")

    def do_POST(self):
        self._forward("POST")

    def do_GET(self):
        self._forward("GET")

    def do_DELETE(self):
        self._forward("DELETE")

    def do_OPTIONS(self):
        self._forward("OPTIONS")


def check(upstream_url: str = DEFAULT_UPSTREAM_URL, db_path: Path | str = DEFAULT_DB_PATH) -> int:
    """Valida token e handshake MCP sem imprimir o segredo."""
    try:
        token = read_member_token(db_path)
    except TokenError as exc:
        print(json.dumps({"status": 401, "error": str(exc)}, ensure_ascii=False))
        return 1
    body = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-11-25",
            "capabilities": {},
            "clientInfo": {"name": "opencode-console-proxy", "version": "1.0"},
        },
    }).encode()
    request = urllib.request.Request(
        upstream_url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Authorization": f"Bearer {token}",
            "Accept-Encoding": "identity",
            "User-Agent": "opencode-console-proxy/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read(4096).decode("utf-8", "replace")
            print(json.dumps(
                {"status": response.status, "server": _server_name(payload)},
                ensure_ascii=False,
            ))
            return 0
    except urllib.error.HTTPError as exc:
        payload = _sanitize(exc.read(512).decode("utf-8", "replace"))
        print(json.dumps({"status": exc.code, "error": payload}, ensure_ascii=False))
        return 1
    except urllib.error.URLError as exc:
        print(json.dumps(
            {"status": 502, "error": f"upstream unavailable: {exc.reason}"},
            ensure_ascii=False,
        ))
        return 1
    except TimeoutError:
        print(json.dumps({"status": 504, "error": "upstream timed out"}, ensure_ascii=False))
        return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="loopback host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="port (default: 8765)")
    parser.add_argument("--upstream-url", default=DEFAULT_UPSTREAM_URL)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--check", action="store_true", help="validate token and handshake")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    if args.check:
        return check(args.upstream_url, args.db)
    if args.host not in {"127.0.0.1", "::1", "localhost"}:
        print("error: proxy must bind to loopback (127.0.0.1 or ::1)", file=sys.stderr)
        return 2

    ProxyHandler.upstream_url = args.upstream_url
    ProxyHandler.db_path = args.db
    server = ThreadingHTTPServer((args.host, args.port), ProxyHandler)
    server.daemon_threads = True
    logging.info("listening on http://%s:%s/mcp -> %s", args.host, args.port, args.upstream_url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
