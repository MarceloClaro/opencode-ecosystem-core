"""Proxy de sessão HTTP/CONNECT: valida destino antes de abrir conexão.

Não é uma fronteira universal de segurança do sistema operacional. Limita o
tráfego enviado por este navegador ao proxy, incluindo cada hop de redirect.
"""
from __future__ import annotations
import asyncio
from urllib.parse import urlsplit


class BrowserOriginProxy:
    def __init__(self, allowed_origins, normalize_origin):
        self.allowed = frozenset(allowed_origins)
        self.normalize = normalize_origin
        self.tasks = set()
        self.decisions = []
        self.decisions_total = 0

    async def __aenter__(self):
        self.server = await asyncio.start_server(self._accept, "127.0.0.1", 0, limit=65536)
        self.url = "http://127.0.0.1:" + str(self.server.sockets[0].getsockname()[1])
        return self

    async def __aexit__(self, *args):
        self.server.close()
        active = list(self.tasks)
        for task in active:
            task.cancel()
        if active:
            await asyncio.gather(*active, return_exceptions=True)
        await self.server.wait_closed()

    def _accept(self, reader, writer):
        # Registrar antes do primeiro await, inclusive peers sem cabeçalho.
        task = asyncio.create_task(self._handle(reader, writer))
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)

    async def _close(self, writer):
        if writer is not None:
            writer.close()
            try:
                await asyncio.wait_for(writer.wait_closed(), 1)
            except (OSError, TimeoutError):
                pass

    async def _pump(self, source, destination):
        while True:
            chunk = await asyncio.wait_for(source.read(65536), 15)
            if not chunk:
                return
            destination.write(chunk)
            await destination.drain()

    async def _handle(self, reader, writer):
        task = asyncio.current_task()
        self.tasks.add(task)
        upstream = None
        try:
            if len(self.tasks) > 32:
                raise ValueError("Limite de conexões de sessão atingido.")
            head = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), 5)
            if len(head) > 65536:
                raise ValueError("Cabeçalho excessivo.")
            lines = head.decode("latin1").split("\r\n")
            method, target, version = lines[0].split(" ")
            if version not in {"HTTP/1.0", "HTTP/1.1"}:
                raise ValueError("Versão HTTP não admitida.")
            url = "https://" + target if method == "CONNECT" else target
            origin = self.normalize(url)
            allowed = origin in self.allowed
            self.decisions_total += 1
            if len(self.decisions) < 128:
                self.decisions.append({"origin": origin, "allowed": allowed, "method": method})
            if not allowed:
                writer.write(b"HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")
                await writer.drain()
                return
            parsed = urlsplit(url)
            if method != "CONNECT" and parsed.scheme != "http":
                raise ValueError("Tráfego HTTPS exige CONNECT.")
            port = parsed.port or (443 if method == "CONNECT" else 80)
            remote_reader, upstream = await asyncio.wait_for(asyncio.open_connection(parsed.hostname, port), 5)
            if method == "CONNECT":
                writer.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
                await writer.drain()
                forward = asyncio.create_task(self._pump(reader, upstream))
                backward = asyncio.create_task(self._pump(remote_reader, writer))
                try:
                    done, pending = await asyncio.wait({forward, backward}, return_when=asyncio.FIRST_COMPLETED)
                    for item in done:
                        item.result()
                finally:
                    forward.cancel()
                    backward.cancel()
                    await asyncio.gather(forward, backward, return_exceptions=True)
                return
            headers = []
            length = 0
            length_seen = False
            for line in lines[1:]:
                if not line:
                    continue
                key, value = line.split(":", 1)
                lower = key.lower()
                if lower in {"transfer-encoding", "upgrade"}:
                    raise ValueError("Upload chunked ou upgrade HTTP não admitido neste proxy.")
                if lower == "content-length":
                    if length_seen or not value.strip().isdigit():
                        raise ValueError("Comprimento de corpo inválido.")
                    length = int(value.strip())
                    length_seen = True
                    if length > 2 * 1024 * 1024:
                        raise ValueError("Corpo excede 2 MiB.")
                if lower not in {"connection", "proxy-connection", "proxy-authorization", "host"}:
                    headers.append(line)
            body = await asyncio.wait_for(reader.readexactly(length), 5) if length else b""
            resource = (parsed.path or "/") + ("?" + parsed.query if parsed.query else "")
            request = "\r\n".join([f"{method} {resource} HTTP/1.1", "Host: " + parsed.netloc,
                                      *headers, "Connection: close", "", ""])
            upstream.write(request.encode("latin1") + body)
            await upstream.drain()
            await self._pump(remote_reader, writer)
        except (OSError, ValueError, TimeoutError, asyncio.IncompleteReadError, asyncio.LimitOverrunError):
            # Mensagem constante: não ecoar URL, headers ou corpo da requisição.
            if not writer.is_closing():
                writer.write(b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")
                try:
                    await writer.drain()
                except OSError:
                    pass
        finally:
            await self._close(upstream)
            await self._close(writer)
            self.tasks.discard(task)
