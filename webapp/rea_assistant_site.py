"""R851: instruções do assistente REA, servidas exclusivamente em loopback.

Não existe API de análise ou de upload. Somente os cinco recursos declarados
podem ser lidos; nenhum caminho da requisição é convertido em caminho de disco.
"""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


_ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/script.js": ("script.js", "text/javascript; charset=utf-8"),
    "/favicon.svg": ("favicon.svg", "image/svg+xml; charset=utf-8"),
}

_CSP = (
    "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; "
    "connect-src 'none'; form-action 'none'; frame-ancestors 'none'; "
    "base-uri 'none'; object-src 'none'"
)


class _InstructionsHandler(BaseHTTPRequestHandler):
    server_version = "REAInstructions/1.0"
    sys_version = ""

    def _respond(self, status, body, media="text/plain; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", media)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Content-Security-Policy", _CSP)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Frame-Options", "DENY")
        if status == 405:
            self.send_header("Allow", "GET")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _local_request(self):
        hosts = self.headers.get_all("Host", [])
        allowed_hosts = {f"127.0.0.1:{self.server.server_port}",
                         f"localhost:{self.server.server_port}"}
        if len(hosts) != 1 or hosts[0] not in allowed_hosts:
            return False
        origins = self.headers.get_all("Origin", [])
        return not origins or (len(origins) == 1 and origins[0] in
                               {f"http://{host}" for host in allowed_hosts})

    def do_GET(self):
        if not self._local_request():
            self._respond(403, "Acesso permitido somente pela origem local.\n".encode())
            return
        # BaseHTTPRequestHandler normaliza barras iniciais duplicadas. A
        # allowlist deve conferir o alvo original, não a versão normalizada.
        path = self.requestline.split()[1]
        if (not path.startswith("/") or path.startswith("//")
                or any(character in path for character in "%?#\\")
                or any(ord(character) < 32 for character in path)
                or any(segment in {".", ".."} for segment in path.split("/"))):
            self._respond(400, "Caminho não canônico recusado.\n".encode())
            return
        asset = self.server.instructions_assets.get(path)
        if asset is None:
            self._respond(404, "Recurso não encontrado.\n".encode())
            return
        body, media = asset
        self._respond(200, body, media)

    def _reject_method(self):
        self._respond(405, "Este site aceita somente GET.\n".encode())

    do_HEAD = do_POST = do_PUT = do_PATCH = do_DELETE = do_OPTIONS = do_TRACE = do_CONNECT = _reject_method

    def log_message(self, format, *args):
        # Não registrar caminhos enviados ao servidor de instruções.
        pass


def make_server(*, port=0) -> HTTPServer:
    """Carrega os recursos permitidos e vincula apenas 127.0.0.1.

    A porta zero seleciona uma porta livre; o chamador controla o ciclo de vida.
    """
    if isinstance(port, bool) or not isinstance(port, int) or not 0 <= port <= 65535:
        raise ValueError("A porta deve ser um inteiro entre 0 e 65535.")
    directory = Path(__file__).with_name("rea_assistant_site")
    if directory.is_symlink():
        raise OSError("Diretório de recursos simbólico recusado.")
    assets = {}
    for route, (filename, media) in _ASSETS.items():
        path = directory / filename
        if path.is_symlink() or not path.is_file():
            raise OSError(f"Recurso local indisponível: {filename}")
        assets[route] = (path.read_bytes(), media)
    server = HTTPServer(("127.0.0.1", port), _InstructionsHandler)
    server.instructions_assets = assets
    return server


def serve_instructions(*, port=8767):
    """Serve instruções locais até interrupção e fecha o socket ao terminar."""
    server = make_server(port=port)
    print(f"Instruções REA: http://127.0.0.1:{server.server_port}/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
